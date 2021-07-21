# -*- coding: utf-8 -*-

{
    'name': 'Informe batch minimo',
    'version': '13.0.1.0',
    'description': '''Informe que permite obtener informacion acerca del acumulado en ordenes de produccion para batch minimo
    ''',
    'category': 'Production',
    'author': 'Gerardo Galindo',
    'depends': [
        'base','mrp','stock',
    ],
    'data': [
        'views/informe_batch_min_view.xml',
        'security/security.xml',
    ],
    'application': False,
    'installable': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',
}