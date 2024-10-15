from odoo.http import request
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta

def prepare_domain_v2(domain):
    if isinstance(domain, tuple) or isinstance(domain, list):
        field_name = domain[0]
        operator = domain[1]
        val = domain[2]

        date_format = '%Y-%m-%d %H:%M:%S'

        current_date = datetime.now()
        current_date = current_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if operator != "date_filter":
            return [tuple(domain)]
        
        if val == "today":
            start_of_today = current_date
            end_of_today = current_date + timedelta(days=1)
            return ["&", (field_name, ">=", start_of_today), (field_name, "<", end_of_today)]
        
        if val == "this_week":
            start_of_week = current_date - timedelta(days=current_date.weekday())
            end_of_week = (current_date + timedelta(days=(7 - current_date.weekday())))
            return ["&", (field_name, ">=", start_of_week), (field_name, "<", end_of_week)]
        
        if val == "this_month":
            start_of_month = current_date.replace(day=1)
            end_of_month = current_date + relativedelta(day=31)
            return ["&", (field_name, ">=", start_of_month), (field_name, "<=", end_of_month)]
        
        if val == "this_quarter":
            start_of_quarter = datetime(current_date.year, ((current_date.month - 1) // 3) * 3 + 1, 1)
            end_of_quarter = start_of_quarter + relativedelta(months=3)
            return ["&", (field_name, '>=', start_of_quarter), (field_name, '<', end_of_quarter)]
            
        if val == "this_year":
            start_of_year = current_date.replace(month=1, day=1)
            end_of_year = start_of_year + relativedelta(years=1)
            return ["&", (field_name, ">=", start_of_year.strftime(date_format)), (field_name, "<", end_of_year.strftime(date_format))]
        
        if val == "last_day":
            start_of_yesterday = current_date - timedelta(days=1)
            return ["&", (field_name, ">=", start_of_yesterday), (field_name, "<", current_date)]

        if val == "last_week":
            end_of_last_week = current_date - timedelta(days=current_date.weekday())
            start_of_last_week = end_of_last_week - timedelta(days=6)
            return ["&", (field_name, ">=", start_of_last_week), (field_name, "<", end_of_last_week)]
        
        if val == "last_month":
            start_of_last_month = (current_date - relativedelta(months=1)).replace(day=1)
            end_of_last_month = start_of_last_month + relativedelta(months=1)
            return ["&", (field_name, ">=", start_of_last_month), (field_name, "<", end_of_last_month)]
        
        if val == "last_quarter":
            start_of_this_quarter = datetime(current_date.year, ((current_date.month - 1) // 3) * 3 + 1, 1)
            end_of_last_quarter = start_of_this_quarter
            start_of_last_quarter = (end_of_last_quarter - relativedelta(months=3)).replace(day=1)
            return ["&", (field_name, ">=", start_of_last_quarter), (field_name, "<", end_of_last_quarter)]
        
        if val == "last_year":
            end_of_last_year = datetime(current_date.year-1, 1, 1)
            start_of_last_year = datetime(current_date.year, 1, 1)
            return ["&", (field_name, ">=", start_of_last_year), (field_name, "<", end_of_last_year)]
        
        if val == "last_7_days":
            start_of_last_7_days = current_date - timedelta(days=6)
            return [(field_name, ">=", start_of_last_7_days)]
        
        if val == "last_30_days":
            start_of_last_30_days = current_date - timedelta(days=29)
            return [(field_name, ">=", start_of_last_30_days)]
        
        if val == "last_90_days":
            start_of_last_90_days = current_date - timedelta(days=89)
            return [(field_name, ">=", start_of_last_90_days)]
        
        if val == "last_365_days":
            start_of_last_365_days = current_date - timedelta(days=364)
            return [(field_name, ">=", start_of_last_365_days)]

        if val == "next_day":
            start_of_next_day = current_date + timedelta(days=1)
            end_of_next_day = start_of_next_day + timedelta(days=1)
            return ["&", (field_name, ">=", start_of_next_day), (field_name, "<", end_of_next_day)]
        
        if val == "next_week":
            start_of_next_week = current_date + timedelta(days=(7 - current_date.weekday()))
            end_of_next_week = start_of_next_week + timedelta(days=7)
            return ["&", (field_name, ">=", start_of_next_week), (field_name, "<", end_of_next_week)]
        
        if val == "next_month":
            start_of_next_month = (current_date + relativedelta(months=1)).replace(day=1)
            end_of_next_month = (start_of_next_month + relativedelta(months=1)).replace(day=1)
            return ["&", (field_name, ">=", start_of_next_month), (field_name, "<", end_of_next_month)]
        
        if val == "next_quarter":
            end_of_quarter = datetime(current_date.year, (((current_date.month - 1) // 3) * 3 + 3)+1, 1)
            start_of_next_quarter = end_of_quarter
            end_of_next_quarter = (start_of_next_quarter + relativedelta(months=3)).replace(day=1)
            return ["&", (field_name, ">=", start_of_next_quarter), (field_name, "<", end_of_next_quarter)]
        
        if val == "next_year":
            start_of_next_year = datetime(current_date.year+1, 1, 1)
            end_of_next_year = datetime(current_date.year+2, 1, 1)
            return ["&", (field_name, ">=", start_of_next_year), (field_name, "<", end_of_next_year)]

    return [tuple(domain)] 