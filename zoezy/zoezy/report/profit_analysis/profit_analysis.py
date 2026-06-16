# Copyright (c) 2026, mukunajohn329@gmail.com and contributors
# For license information, please see license.txt

from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import date, timedelta

import frappe
from frappe import _
from frappe.utils import (
    add_to_date,
    flt,
    get_first_day,
    get_last_day,
    get_year_ending,
    get_year_start,
    getdate,
    nowdate,
)

PERIODICITIES = ("Yearly", "Monthly", "Weekly", "Date Range")


@dataclass
class ProfitAnalysisFilters:
    """Typed view over the raw filter dict coming from the report UI."""

    periodicity: str = "Monthly"
    from_date: str | None = None
    to_date: str | None = None
    client: str | None = None
    subscription: str | None = None
    status: str | None = None
    chart_type: str = "Bar"

    @classmethod
    def from_dict(cls, raw: dict | None) -> "ProfitAnalysisFilters":
        raw = raw or {}
        allowed = {f.name for f in fields(cls)}
        instance = cls(**{k: v for k, v in raw.items() if k in allowed})
        instance._normalise()
        return instance

    def _normalise(self) -> None:
        if self.periodicity not in PERIODICITIES:
            self.periodicity = "Monthly"

        self.to_date = getdate(self.to_date) if self.to_date else getdate(nowdate())
        self.from_date = (
            getdate(self.from_date) if self.from_date else get_year_start(self.to_date)
        )

        if self.from_date > self.to_date:
            frappe.throw(_("From Date cannot be after To Date."))

    def invoice_conditions(self) -> dict:
        """Filters applied to the Client Invoice query."""
        conditions: dict = {
            "docstatus": 1,
            "posting_date": ["between", [self.from_date, self.to_date]],
        }
        if self.client:
            conditions["client"] = self.client
        if self.subscription:
            conditions["subscription"] = self.subscription
        if self.status:
            conditions["status"] = self.status
        return conditions


@dataclass
class ProfitAnalysisRow:
    """A single period bucket in the report."""

    period: str
    start: date
    end: date
    invoice_count: int = 0
    invoiced: float = 0.0
    outstanding: float = 0.0

    @property
    def collected(self) -> float:
        return flt(self.invoiced - self.outstanding, 2)

    @property
    def collection_rate(self) -> float:
        return flt(self.collected / self.invoiced * 100, 2) if self.invoiced else 0.0

    def contains(self, posting_date: date) -> bool:
        return self.start <= posting_date <= self.end

    def add_invoice(self, total: float, outstanding: float) -> None:
        self.invoice_count += 1
        self.invoiced = flt(self.invoiced + total, 2)
        self.outstanding = flt(self.outstanding + outstanding, 2)

    def as_dict(self) -> dict:
        return {
            "period": self.period,
            "invoice_count": self.invoice_count,
            "invoiced": self.invoiced,
            "collected": self.collected,
            "outstanding": self.outstanding,
            "collection_rate": self.collection_rate,
        }


def execute(filters: dict | None = None):
    """Main entry point. Returns (columns, data, message, chart, summary)."""
    parsed = ProfitAnalysisFilters.from_dict(filters)
    rows = build_rows(parsed)
    data = [row.as_dict() for row in rows]
    return get_columns(), data, None, get_chart(rows, parsed), get_report_summary(rows)


def get_columns() -> list[dict]:
    return [
        {
            "label": _("Period"),
            "fieldname": "period",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Invoices"),
            "fieldname": "invoice_count",
            "fieldtype": "Int",
            "width": 90,
        },
        {
            "label": _("Invoiced"),
            "fieldname": "invoiced",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Collected"),
            "fieldname": "collected",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Outstanding"),
            "fieldname": "outstanding",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": _("Collection %"),
            "fieldname": "collection_rate",
            "fieldtype": "Percent",
            "width": 110,
        },
    ]


def get_chart(
    rows: list[ProfitAnalysisRow], filters: ProfitAnalysisFilters
) -> dict | None:
    """Collected vs outstanding per period, with an invoiced reference line."""
    if not rows:
        return None

    chart_type = "line" if filters.chart_type == "Line" else "bar"
    return {
        "data": {
            "labels": [row.period for row in rows],
            "datasets": [
                {"name": _("Collected"), "values": [row.collected for row in rows]},
                {"name": _("Outstanding"), "values": [row.outstanding for row in rows]},
                {
                    "name": _("Invoiced"),
                    "values": [row.invoiced for row in rows],
                    "chartType": "line",
                },
            ],
        },
        "type": chart_type,
        "barOptions": {"stacked": True},
        "colors": ["#28a745", "#dc3545", "#5e64ff"],
        "fieldtype": "Currency",
    }


def get_report_summary(rows: list[ProfitAnalysisRow]) -> list[dict]:
    """Headline numbers shown above the report."""
    invoiced = flt(sum(row.invoiced for row in rows), 2)
    collected = flt(sum(row.collected for row in rows), 2)
    outstanding = flt(sum(row.outstanding for row in rows), 2)
    rate = flt(collected / invoiced * 100, 2) if invoiced else 0.0

    return [
        {
            "label": _("Total Invoiced"),
            "value": invoiced,
            "datatype": "Currency",
            "indicator": "Blue",
        },
        {
            "label": _("Total Collected"),
            "value": collected,
            "datatype": "Currency",
            "indicator": "Green",
        },
        {
            "label": _("Outstanding"),
            "value": outstanding,
            "datatype": "Currency",
            "indicator": "Red",
        },
        {
            "label": _("Collection Rate"),
            "value": rate,
            "datatype": "Percent",
            "indicator": "Green" if rate >= 75 else "Orange",
        },
    ]


def build_rows(filters: ProfitAnalysisFilters) -> list[ProfitAnalysisRow]:
    buckets = build_buckets(filters)
    invoices = frappe.get_all(
        "Client Invoice",
        filters=filters.invoice_conditions(),
        fields=["posting_date", "total", "outstanding_amount"],
    )

    for invoice in invoices:
        posting_date = getdate(invoice.posting_date)
        for bucket in buckets:
            if bucket.contains(posting_date):
                bucket.add_invoice(flt(invoice.total), flt(invoice.outstanding_amount))
                break

    # Drop empty buckets so the report stays readable.
    return [bucket for bucket in buckets if bucket.invoice_count]


def build_buckets(filters: ProfitAnalysisFilters) -> list[ProfitAnalysisRow]:
    """Generate contiguous period buckets spanning the filter date range."""
    start, end = filters.from_date, filters.to_date

    if filters.periodicity == "Date Range":
        label = f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"
        return [ProfitAnalysisRow(period=label, start=start, end=end)]

    buckets: list[ProfitAnalysisRow] = []
    cursor = period_start(start, filters.periodicity)

    while cursor <= end:
        bucket_start = max(cursor, start)
        bucket_end = min(period_end(cursor, filters.periodicity), end)
        buckets.append(
            ProfitAnalysisRow(
                period=period_label(cursor, filters.periodicity),
                start=bucket_start,
                end=bucket_end,
            )
        )
        cursor = next_period(cursor, filters.periodicity)

    return buckets


def period_start(dt: date, periodicity: str) -> date:
    if periodicity == "Yearly":
        return get_year_start(dt)
    if periodicity == "Monthly":
        return get_first_day(dt)
    # Weekly: align to Monday.
    return dt - timedelta(days=dt.weekday())


def period_end(dt: date, periodicity: str) -> date:
    if periodicity == "Yearly":
        return get_year_ending(dt)
    if periodicity == "Monthly":
        return get_last_day(dt)
    return dt + timedelta(days=6 - dt.weekday())


def next_period(dt: date, periodicity: str) -> date:
    if periodicity == "Yearly":
        return getdate(add_to_date(period_start(dt, periodicity), years=1))
    if periodicity == "Monthly":
        return getdate(add_to_date(period_start(dt, periodicity), months=1))
    return period_start(dt, periodicity) + timedelta(days=7)


def period_label(dt: date, periodicity: str) -> str:
    if periodicity == "Yearly":
        return dt.strftime("%Y")
    if periodicity == "Monthly":
        return dt.strftime("%b %Y")
    week_start = period_start(dt, periodicity)
    week_end = period_end(dt, periodicity)
    return f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}"
