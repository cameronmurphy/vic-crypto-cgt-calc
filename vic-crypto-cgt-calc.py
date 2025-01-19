#!/usr/bin/env python3

import argparse

TAX_BRACKETS = {
    18201: 0.16,
    45001: 0.30,
    135001: 0.37,
    190001: 0.45,
}
MEDICARE_LEVY = 0.02


def calculate_cgt(income, taxable_component):
    cgt = 0
    current_bracket_dollars_floor, current_bracket_percent = 0, 0
    iterator = iter(TAX_BRACKETS.items())

    # Find the current bracket that income places us in
    while True:
        next_bracket_dollars_floor, next_bracket_percent = next(iterator, [None, None])

        if next_bracket_dollars_floor is not None and income > next_bracket_dollars_floor:
            current_bracket_dollars_floor, current_bracket_percent = next_bracket_dollars_floor, next_bracket_percent
        else:
            break

    while taxable_component > 0:
        current_bracket_component = taxable_component

        # If there's not enough room to consume taxable_component all within this bracket, enforce a limit
        if next_bracket_dollars_floor is not None and next_bracket_dollars_floor - income < taxable_component:
            current_bracket_component = next_bracket_dollars_floor - income

        # Income is consumed by first bracket
        income = 0
        cgt += current_bracket_component * (current_bracket_percent + MEDICARE_LEVY)
        taxable_component -= current_bracket_component

        current_bracket_dollars_floor, current_bracket_percent = next_bracket_dollars_floor, next_bracket_percent
        next_bracket_dollars_floor, next_bracket_percent = next(iterator, [None, None])

    return cgt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--income', type=float, required=True)
    parser.add_argument('--buy-price', type=float, required=True)
    parser.add_argument('--sell-price', type=float, required=True)
    parser.add_argument('--quantity', type=float, required=True)
    parser.add_argument('--trade-fee-percent', type=float, required=True)
    parser.add_argument('--cgt-discount', action='store_true')
    args = parser.parse_args()

    income = float(args.income)
    sell_price = float(args.sell_price)
    quantity = float(args.quantity)
    original_investment = float(args.buy_price) * quantity
    trade_fee_percent = float(args.trade_fee_percent)

    cash_from_sale_before_fees = sell_price * quantity
    print('Cash from sale before trade fee:  ${:,.2f}'.format(cash_from_sale_before_fees))

    trade_fee = cash_from_sale_before_fees * trade_fee_percent / 100
    print('Trade fee:                        ${:,.2f}'.format(trade_fee))

    cash_from_sale = cash_from_sale_before_fees - trade_fee
    print('Cash from sale:                   ${:,.2f}'.format(cash_from_sale))

    total_capital_gains = cash_from_sale - original_investment
    print('Total capital gains:              ${:,.2f}'.format(total_capital_gains))

    taxable_component_percent = 50 if args.cgt_discount else 100
    taxable_component = total_capital_gains * taxable_component_percent / 100
    print('Taxable component ({}%):{}         ${:,.2f}'.format(
        taxable_component_percent,
        ' ' if args.cgt_discount else '',
        taxable_component,
    ))

    total_cgt = calculate_cgt(income, taxable_component)
    print('Total CGT:                        ${:,.2f}'.format(total_cgt))

    cash_after_cgt = cash_from_sale - total_cgt
    print('Cash after CGT:                   ${:,.2f}'.format(cash_after_cgt))


if __name__ == '__main__':
    main()
