# Copyright 2009 Camptocamp
# Copyright 2009 Grzegorz Grzelak
# Copyright 2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import xml.sax
from collections import defaultdict
from datetime import date, timedelta
from urllib.request import urlopen

from odoo import fields, models


class ResCurrencyRateProviderECB(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("ECB", "European Central Bank")],
        ondelete={"ECB": "set default"},
    )

    def _get_close_time(self):
        """According to ECB closing time, today's rate data will only be available
        from 17:30 CET.
        https://www.ecb.europa.eu/services/contacts/working-hours/html/index.en.html

        It is necessary to define a blocking time to avoid the following use case:
        - Cron record call webservice today BEFORE time x.
        - The webservice response will not give an error but it will not return data
        for today.
        - The value of last_successful_run will be updated with today's date.
        - The value of next_run will be updated to tomorrow.

        You would never get the value for today and tomorrow the same thing would happen.

        CET Time is UTC+2 in summer and UTC+1 in winter:
        (https://en.wikipedia.org/wiki/Central_European_Time).
        Block time must be set to UTC+0
        """
        if self.service == "ECB":
            return 19  # 18:30
        return super()._get_close_time()

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "ECB":
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip
        return [
            "USD",
            "JPY",
            "BGN",
            "CYP",
            "CZK",
            "DKK",
            "EEK",
            "GBP",
            "HUF",
            "LTL",
            "LVL",
            "MTL",
            "PLN",
            "ROL",
            "RON",
            "SEK",
            "SIT",
            "SKK",
            "CHF",
            "ISK",
            "NOK",
            "HRK",
            "RUB",
            "TRL",
            "TRY",
            "AUD",
            "BRL",
            "CAD",
            "CNY",
            "HKD",
            "IDR",
            "ILS",
            "INR",
            "KRW",
            "MXN",
            "MYR",
            "NZD",
            "PHP",
            "SGD",
            "THB",
            "ZAR",
            "EUR",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "ECB":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover
        invert_calculation = False
        if base_currency != "EUR":
            invert_calculation = True
            if base_currency not in currencies:
                currencies.append(base_currency)

        # Depending on the date range, different URLs are used
        url = "https://www.ecb.europa.eu/stats/eurofxref"
        if date_from == date_to and date_from == date.today():
            url = url + "/eurofxref-daily.xml"
        elif (date.today() - date_from) / timedelta(days=90) < 1.0:
            url = url + "/eurofxref-hist-90d.xml"
        else:
            url = url + "/eurofxref-hist.xml"

        handler = EcbRatesHandler(currencies, date_from, date_to)
        with urlopen(url) as response:
            xml.sax.parse(response, handler)
        content = handler.content
        if invert_calculation:
            for k in content.keys():
                base_rate = float(content[k][base_currency])
                for rate in content[k].keys():
                    content[k][rate] = str(float(content[k][rate]) / base_rate)
                content[k]["EUR"] = str(1.0 / base_rate)
        return content


class EcbRatesHandler(xml.sax.ContentHandler):
    def __init__(self, currencies, date_from, date_to):
        self.currencies = currencies
        self.date_from = date_from
        self.date_to = date_to
        self.date = None
        self.content = defaultdict(dict)

    def startElement(self, name, attrs):
        if name == "Cube" and "time" in attrs:
            self.date = fields.Date.from_string(attrs["time"])
        elif name == "Cube" and all([x in attrs for x in ["currency", "rate"]]):
            currency = attrs["currency"]
            rate = attrs["rate"]
            if (
                (self.date_from is None or self.date >= self.date_from)
                and (self.date_to is None or self.date <= self.date_to)
                and currency in self.currencies
            ):
                self.content[self.date.isoformat()][currency] = rate
