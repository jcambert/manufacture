# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError, ValidationError
from random import randint
from ast import literal_eval as _literal_eval
import logging

_logger = logging.getLogger(__name__)

def literal_eval(arg):
    if isinstance(arg,bool):
        return arg
    return _literal_eval(arg)

class Model(models.AbstractModel):
    """ Main super-class for regular database-persisted Odoo models.
    Odoo models are created by inheriting from this class::
        class user(Model):
            ...
    The system will later instantiate the class once per database (on
    which the class' module is installed).
    """
    # _auto = False                # automatically create database backend
    # _register = False           # not visible in ORM registry, meant to be python-inherited only
    # _abstract = False           # not abstract
    # _transient = False          # not transient
    _name = 'model.mixin'
    _description = 'Model Mixin'
    _models= {}
    # @classmethod
    # def _build_model(self, pool, cr):
    #     super(models.AbstractModel,self)._build_model(pool,cr)
    #     self._models.update(_inner_models)
    def get_param(self,key):
        return literal_eval( self.env['ir.config_parameter'].get_param(key) or False)

    """def __getattr__(self,key):
        # print(key)
        try:
            if isinstance(key,str) and key in self._models:
                return self.env[self._models[key]]
            res =super(models.AbstractModel,self).__getattr__(key)
        except AttributeError as ex:
            print(ex)
            print(key)
    """

    def map(self,fn):
        return map(fn,self)