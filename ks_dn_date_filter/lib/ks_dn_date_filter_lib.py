from odoo.fields import datetime
from datetime import timedelta

from odoo.addons.ks_dashboard_ninja.lib import ks_date_filter_selections



def ks_date_series_l(ks_date_selection):
    ks_date_data = {}
    date_filter_options = {
        'day': 0,
        'week': 7,
        'month': 30,
        'quarter': 90,
        'half': 180,
        'year': 365,
        'past': False,
        'future': False
    }
    ks_date_data["selected_end_date"] = datetime.strptime(datetime.now().strftime("%Y-%m-%d 23:59:59"),
                                                          '%Y-%m-%d %H:%M:%S')
    ks_date_data["selected_start_date"] = datetime.strptime((datetime.now() - timedelta(
        days=date_filter_options[ks_date_selection])).strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')
    return ks_date_data

ks_date_filter_selections.ks_date_series_l  = ks_date_series_l