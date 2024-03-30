# -*- coding: utf-8 -*-

from odoo import models


class IrHttp(models.AbstractModel):
    """
    Overwrite to add custom modules to translation
    """
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return mods + ["documentation_builder"]
