import os
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify
from scipy.integrate import odeint
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'DataSetCvd.xlsx')
CACHE_PATH = os.path.join(BASE_DIR, 'model_cache.json')

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

N_TOTAL = 48274162.0
SIGMA_DEFAULT = 1.0 / 5.2
DELTA_DEFAULT = 0.0012

def seirv_ode(y, t, N_eff, beta, sigma, gamma, delta, nu):
    S, E, I, R, V = y
    dSdt = -(beta * S * I) / N_eff - nu * S
    dEdt = (beta * S * I) / N_eff - sigma * E
    dIdt = sigma * E - gamma * I - delta * I
    dRdt = gamma * I
    dVdt = nu * S
    return [dSdt, dEdt, dIdt, dRdt, dVdt]

def load_and_calibrate():
    # Gunakan cache jika sudah tersedia untuk cold start cepat (misal di Vercel Serverless)
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: gagal membaca cache ({e}), menjalankan kalibrasi ulang...")

    df_wj = pd.read_excel(DATA_PATH, sheet_name='WJ_200304_221002')
    df_vacc = pd.read_excel(DATA_PATH, sheet_name='INA_Vacc')

    df_wj['Tanggal'] = pd.to_datetime(df_wj['Tanggal'])
    df_vacc['Date'] = pd.to_datetime(df_vacc['Date'])

    df = pd.merge(df_wj, df_vacc[['Date', 'Vacc_1', 'Vacc_2']], left_on='Tanggal', right_on='Date', how='left')
    sub = df[(df['Tanggal'] >= '2021-06-05') & (df['Tanggal'] <= '2021-09-10')].copy().reset_index(drop=True)

    for col in ['Confirmed_active', 'Confirmed_recovered', 'Confirmed_deaths', 'Vacc_2']:
        sub[col] = sub[col].interpolate().bfill().ffill()

    sub['Vacc_Jabar'] = sub['Vacc_2'] * 0.178

    dates = sub['Tanggal'].dt.strftime('%Y-%m-%d').tolist()
    i_obs = sub['Confirmed_active'].values.astype(float)
    r_obs = sub['Confirmed_recovered'].values.astype(float)
    v_obs = sub['Vacc_Jabar'].values.astype(float)
    t = np.arange(len(sub))

    i0 = float(i_obs[0])
    r0_init = float(r_obs[0])
    v0_init = float(v_obs[0])

    def loss(params):
        beta, gamma, nu, n_scale = params
        n_eff = N_TOTAL * n_scale
        e0 = i0 * 0.85
        r0_s = r0_init * n_scale
        v0_s = v0_init * n_scale
        s0 = max(n_eff - e0 - i0 - r0_s - v0_s, i0 * 5)
        sol = odeint(seirv_ode, [s0, e0, i0, r0_s, v0_s], t, args=(n_eff, beta, SIGMA_DEFAULT, gamma, DELTA_DEFAULT, nu))
        return np.mean((sol[:, 2] - i_obs) ** 2)

    res = minimize(loss, [0.40, 0.12, 0.004, 0.04],
                   bounds=[(0.05, 1.5), (0.04, 0.30), (0.0005, 0.04), (0.01, 0.5)],
                   method='L-BFGS-B')
    beta_opt, gamma_opt, nu_opt, scale_opt = [float(x) for x in res.x]

    n_eff_opt = N_TOTAL * scale_opt
    e0_opt = i0 * 0.85
    r0_opt = r0_init * scale_opt
    v0_opt = v0_init * scale_opt
    s0_opt = max(n_eff_opt - e0_opt - i0 - r0_opt - v0_opt, i0 * 5)

    sol_base = odeint(seirv_ode, [s0_opt, e0_opt, i0, r0_opt, v0_opt], t,
                      args=(n_eff_opt, beta_opt, SIGMA_DEFAULT, gamma_opt, DELTA_DEFAULT, nu_opt))
    i_pred_base = sol_base[:, 2]

    r2_val = float(r2_score(i_obs, i_pred_base))
    mape_val = float(np.mean(np.abs((i_obs - i_pred_base) / i_obs)) * 100)
    rmse_val = float(np.sqrt(mean_squared_error(i_obs, i_pred_base)))

    return {
        'dates': dates,
        'actual_active': [int(round(x)) for x in i_obs],
        'actual_recovered': [int(round(x)) for x in r_obs],
        'actual_vacc': [int(round(x)) for x in v_obs],
        'peak_actual': int(round(i_obs.max())),
        'peak_actual_date': dates[int(np.argmax(i_obs))],
        'n_eff': n_eff_opt,
        'init_state': [s0_opt, e0_opt, i0, r0_opt, v0_opt],
        'beta_opt': round(beta_opt, 4),
        'gamma_opt': round(gamma_opt, 4),
        'sigma_opt': round(SIGMA_DEFAULT, 4),
        'nu_opt': round(nu_opt, 5),
        'r2': round(r2_val, 3),
        'mape': round(mape_val, 2),
        'rmse': round(rmse_val, 1)
    }

MODEL_CONTEXT = load_and_calibrate()

def run_ode(beta, sigma, gamma, nu, days=None):
    if days is None:
        days = len(MODEL_CONTEXT['dates'])
    t = np.arange(days)
    sol = odeint(seirv_ode, MODEL_CONTEXT['init_state'], t,
                 args=(MODEL_CONTEXT['n_eff'], beta, sigma, gamma, DELTA_DEFAULT, nu))
    return {
        'S': [int(round(x)) for x in sol[:, 0]],
        'E': [int(round(x)) for x in sol[:, 1]],
        'I': [int(round(x)) for x in sol[:, 2]],
        'R': [int(round(x)) for x in sol[:, 3]],
        'V': [int(round(x)) for x in sol[:, 4]],
    }

@app.route('/')
def index():
    return render_template('index.html', ctx=MODEL_CONTEXT)

@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    payload = request.get_json(force=True)
    nu = float(payload.get('nu', MODEL_CONTEXT['nu_opt']))
    beta = float(payload.get('beta', MODEL_CONTEXT['beta_opt']))
    gamma = float(payload.get('gamma', MODEL_CONTEXT['gamma_opt']))
    sigma = float(payload.get('sigma', MODEL_CONTEXT['sigma_opt']))

    sim_current = run_ode(beta, sigma, gamma, nu)
    sim_novacc = run_ode(beta, sigma, gamma, 0.0)

    peak_curr = max(sim_current['I'])
    peak_novacc = max(sim_novacc['I'])
    peak_idx = int(np.argmax(sim_current['I']))
    peak_date = MODEL_CONTEXT['dates'][peak_idx]
    reduction = ((peak_novacc - peak_curr) / peak_novacc * 100.0) if peak_novacc > 0 else 0.0
    r0 = beta / (gamma + DELTA_DEFAULT)

    # Compare 4 policy scenarios dynamically
    scenario_defs = [
        {'id': 'novacc', 'name': 'Tanpa Intervensi Vaksin', 'tag': 'Kontrol (0×)', 'nu': 0.0, 'tone': 'slate'},
        {'id': 'baseline', 'name': 'Baseline Historis Jabar', 'tag': 'Aktual (1×)', 'nu': MODEL_CONTEXT['nu_opt'], 'tone': 'ice'},
        {'id': 'moderat', 'name': 'Percepatan Moderat', 'tag': 'Optimasi (3×)', 'nu': round(MODEL_CONTEXT['nu_opt'] * 3, 5), 'tone': 'lime'},
        {'id': 'agresif', 'name': 'Percepatan Agresif', 'tag': 'Intensif (6×)', 'nu': round(MODEL_CONTEXT['nu_opt'] * 6, 5), 'tone': 'dark'}
    ]

    scenarios_out = []
    for sc in scenario_defs:
        res_sc = run_ode(beta, sigma, gamma, sc['nu'])
        pk = max(res_sc['I'])
        pk_d = MODEL_CONTEXT['dates'][int(np.argmax(res_sc['I']))]
        end_i = res_sc['I'][-1]
        end_v = res_sc['V'][-1]
        red_pct = ((peak_novacc - pk) / peak_novacc * 100.0) if peak_novacc > 0 else 0.0
        scenarios_out.append({
            'id': sc['id'],
            'name': sc['name'],
            'tag': sc['tag'],
            'nu': sc['nu'],
            'peak': pk,
            'peak_date': pk_d,
            'end_active': end_i,
            'end_vacc': end_v,
            'reduction': round(red_pct, 1),
            'tone': sc['tone']
        })

    return jsonify({
        'current': sim_current,
        'novacc_I': sim_novacc['I'],
        'metrics': {
            'peak_curr': peak_curr,
            'peak_date': peak_date,
            'peak_novacc': peak_novacc,
            'reduction': round(reduction, 1),
            'r0': round(r0, 2),
            'end_active': sim_current['I'][-1],
            'end_vacc': sim_current['V'][-1]
        },
        'scenarios': scenarios_out
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
