# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS document migrator API."""

import json
import logging

import click
from elasticsearch_dsl import Q
from invenio_app_ils.errors import IlsValidationError
from invenio_app_ils.proxies import current_app_ils

from cds_ils.migrator.api import bulk_index_records, \
    import_document_from_dump, import_record, model_provider_by_rectype
from cds_ils.migrator.errors import DocumentMigrationError

migrated_logger = logging.getLogger("migrated_records")
records_logger = logging.getLogger("records_errored")


def import_documents_from_record_file(sources, include):
    """Import documents from records file generated by CDS-Migrator-Kit."""
    include = include if include is None else include.split(",")
    records = []
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        model, provider = model_provider_by_rectype("document")
        include_keys = None if include is None else include.split(",")
        with click.progressbar(json.load(source).items()) as bar:
            records = []
            for key, parent in bar:
                click.echo(
                    'Importing document "{}"...'.format(parent["legacy_recid"])
                )
                if include_keys is None or key in include_keys:
                    record = import_record(parent, model, provider)
                    records.append(record)
    # Index all new parent records
    bulk_index_records(records)


def import_documents_from_dump(sources, source_type, eager, include):
    """Load records."""
    include = include if include is None else include.split(",")
    for idx, source in enumerate(sources, 1):
        click.echo(
            "({}/{}) Migrating documents in {}...".format(
                idx, len(sources), source.name
            )
        )
        data = json.load(source)
        with click.progressbar(data) as records:
            for item in records:
                click.echo('Processing document "{}"...'.format(item["recid"]))
                if include is None or str(item["recid"]) in include:
                    try:
                        import_document_from_dump(
                            item, source_type, eager=eager
                        )

                        migrated_logger.warning(
                            "#RECID {0}: OK".format(item["recid"])
                        )
                    except IlsValidationError as e:
                        records_logger.error(
                            "@RECID: {0} FATAL: {1}".format(
                                item["recid"],
                                str(e.original_exception.message),
                            )
                        )
                    except Exception as e:
                        records_logger.error(
                            "@RECID: {0} ERROR: {1}".format(
                                item["recid"], str(e)
                            )
                        )


def get_document_by_barcode(barcode, legacy_recid):
    """Return document from barcode search."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()
    search = document_search.query(
        "query_string", query='_migration.items.barcode:"{}"'.format(barcode)
    )

    result = search.execute()
    hits_total = result.hits.total.value

    if hits_total == 1:
        click.secho(
            "! document found with item barcode {}".format(barcode),
            fg="green",
        )
        return document_class.get_record_by_pid(result.hits[0].pid)

    else:
        click.secho(
            "no document found with barcode {}".format(barcode),
            fg="red",
        )
        raise DocumentMigrationError(
            "found more than one document with barcode {}".format(barcode)
        )


def get_document_by_legacy_recid(legacy_recid):
    """Search documents by its legacy recid."""
    document_class = current_app_ils.document_record_cls
    document_search = current_app_ils.document_search_cls()

    search = document_search.query(
        "bool", filter=[Q("term", legacy_recid=legacy_recid)]
    )
    result = search.execute()
    hits_total = result.hits.total.value

    if hits_total == 1:
        click.secho(
            "! document found with legacy recid {}".format(legacy_recid),
            fg="green",
        )
        return document_class.get_record_by_pid(result.hits[0].pid)

    elif hits_total == 0:
        click.secho(
            "no document found with legacy recid {}".format(legacy_recid),
            fg="red",
        )
        raise DocumentMigrationError(
            "no document found with legacy recid {}".format(legacy_recid)
        )
    else:
        click.secho(
            "no document found with legacy recid {}".format(legacy_recid),
            fg="red",
        )
        raise DocumentMigrationError(
            "found more than one document with recid {}".format(legacy_recid)
        )


def get_all_documents_with_files():
    """Return all documents with files to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            Q("term", _migration__has_files=True),
        ],
    )
    return search


def get_documents_with_proxy_eitems():
    """Return documents with eitems behind proxy to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            Q("term", _migration__eitems_has_proxy=True),
        ],
    )
    return search


def get_documents_with_ebl_eitems():
    """Return documents with eitems from EBL provider to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            Q("term", _migration__eitems_has_ebl=True),
        ],
    )
    return search


def get_documents_with_external_eitems():
    """Return documents with eitems from external providers to be migrated."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            Q("term", _migration__eitems_has_external=True),
        ],
    )
    return search


def search_documents_with_siblings_relations():
    """Return documents with siblings relations."""
    document_search = current_app_ils.document_search_cls()
    search = document_search.filter(
        "bool",
        filter=[
            Q("term", _migration__has_related=True),
        ],
    )
    return search
