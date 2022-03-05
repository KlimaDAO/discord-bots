import os
from pyairtable import Table
from pyairtable.formulas import match
from collections import namedtuple

# Initiallize Airtable
api_key = os.environ['AIRTABLE_API_KEY']

alerts_app = 'appTX60pjw7iWGz4Y'
alerts_table = 'tblkVGjvsmwrI7vMn'
master_data_app = 'appAQXkU6sdPuQ1p6'
bonds_table = 'tbl5zIl9EZKaras54'

alert_db = Table(api_key, alerts_app, alerts_table)
bond_db = Table(api_key, master_data_app, bonds_table)

Bond = namedtuple("Bond", "bond price_usd discount max_purchase debt_reached")
Alert = namedtuple("Alert", "bond discount user")


def search_alert(table: Table, search_bond: str = None, search_user: str = None, search_discount: float = None, search_active: bool = None, search_type: str = None):   # noqa: E501
    if search_type == 'triggered':
        if search_bond is not None and search_discount is not None:
            formula = "AND({active}=1,{bond}='"+str(search_bond)+"',{discount}<='"+str(search_discount)+"')"   # noqa: E501
    elif search_type == 'reactivate':
        if search_bond is not None and search_discount is not None:
            formula = "AND({active}=0,{bond}='"+str(search_bond)+"',{discount}>'"+str(search_discount)+"')"   # noqa: E501
    else:
        if search_bond is not None and search_user is not None and search_discount is not None:
            formula = "AND({bond}='"+str(search_bond)+"',{user}='"+str(search_user)+"',{discount}<='"+str(search_discount)+"')"   # noqa: E501
        elif search_user is not None and search_discount is not None:
            formula = "AND({user}='"+str(search_user)+"',{discount}<='"+str(search_discount)+"')"
        elif search_bond is not None and search_user is not None:
            formula = match({'bond': search_bond, 'user': search_user})
        elif search_bond is not None:
            formula = match({'bond': search_bond})
        elif search_user is not None:
            formula = match({'user': search_user})
        elif search_discount is not None:
            formula = "AND({discount}<='"+str(search_discount)+"')"

    r = table.all(formula=formula)
    rr = []
    if r is not None:
        for a in r:
            rr.append(Alert(a['fields']['bond'], a['fields']['discount'], a['fields']['user']))

        return(rr)


def activate_alert(table: Table, search_bond: str, search_user: str, search_discount: float):
    formula = match({'bond': search_bond, 'user': search_user, 'discount': search_discount})
    r = table.first(formula=formula)
    table.update(r['id'], {'active': True})


def deactivate_alert(table: Table, search_bond: str, search_user: str, search_discount: float):
    formula = match({'bond': search_bond, 'user': search_user, 'discount': search_discount})
    r = table.first(formula=formula)
    table.update(r['id'], {'active': False})


def fetch_bond_md(table: Table, search_bond: str):
    formula = match({'bond': search_bond, 'active': True})
    r = table.first(formula=formula)
    if r is not None:
        return(r['fields']['address'], r['fields']['abi'])


def fetch_bond_info(table: Table, search_bond: str):
    formula = match({'bond': search_bond, 'active': True})
    r = table.first(formula=formula)
    if r is not None:
        if 'debt_reached' in r['fields']:
            return(Bond(r['fields']['bond'], r['fields']['price_usd'], r['fields']['discount'], r['fields']['max_purchase'], r['fields']['debt_reached']))   # noqa: E501
        else:
            return(Bond(r['fields']['bond'], r['fields']['price_usd'], r['fields']['discount'], r['fields']['max_purchase'], False))   # noqa: E501


def active_bonds(table: Table):
    formula = match({'active': True})
    r = table.all(formula=formula)
    if r is not None:
        rr = []
        for b in r:
            rr.append(b['fields']['bond'])
        return(rr)


def update_bond_info(table: Table, update_bond: str, update_price: float, update_disc: float, update_capacity: float, update_debt: bool):   # noqa: E501
    formula = match({'bond': update_bond})
    r = table.first(formula=formula)
    table.update(r['id'], {'price_usd': update_price, 'discount': update_disc, 'max_purchase': update_capacity, 'debt_reached': update_debt})   # noqa: E501


def add_alert(table: Table, add_bond: str, add_discount: float, add_user: str):
    bond_check = fetch_bond_info(bond_db, add_bond)
    if bond_check is not None:
        alert_check = search_alert(table, search_user=add_user)
        if len(alert_check) < 5:
            for a in alert_check:
                if a == (add_bond, float(add_discount), add_user):
                    # Alert already configured
                    return(0)

            # All checks passed, create alert
            try:
                table.create({'bond': add_bond, 'user': add_user, 'discount': add_discount})
                return(1)
            except Exception as e:
                print(e)
                return(-999)

        else:
            # User already has 5 alerts configured
            return(-1)
    else:
        # Bond does not exist or not active anymore
        return(-2)


def remove_alert(table: Table, delete_bond: str, delete_discount: float, delete_user: str):
    formula = match({'bond': delete_bond, 'user': delete_user, 'discount': delete_discount})
    r = table.first(formula=formula)
    if r is not None:
        try:
            table.delete(r['id'])
            return(1)
        except Exception as e:
            print(e)
            return(-999)
    else:
        # Alert does not exist
        return(0)
