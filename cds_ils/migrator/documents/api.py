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
from invenio_app_ils.documents.api import Document, DocumentIdProvider
from invenio_app_ils.documents.search import DocumentSearch
from invenio_app_ils.errors import IlsValidationError
from invenio_migrator.cli import _loadrecord

from cds_ils.migrator.api import bulk_index_records, import_record, \
    model_provider_by_rectype
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
                        _loadrecord(item, source_type, eager=eager)

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


def get_document_by_legacy_recid(legacy_recid):
    """Search documents by its legacy recid."""
    search = DocumentSearch().query(
        "bool", filter=[Q("term", legacy_recid=legacy_recid)]
    )
    result = search.execute()
    hits_total = result.hits.total.value
    if not result.hits or hits_total < 1:
        click.secho(
            "no document found with legacy recid {}".format(legacy_recid),
            fg="red",
        )
        raise DocumentMigrationError(
            "no document found with legacy recid {}".format(legacy_recid)
        )
    elif hits_total > 1:
        click.secho(
            "no document found with legacy recid {}".format(legacy_recid),
            fg="red",
        )
        raise DocumentMigrationError(
            "found more than one document with recid {}".format(legacy_recid)
        )
    else:
        click.secho(
            "! document found with legacy recid {}".format(legacy_recid),
            fg="green",
        )
        return Document.get_record_by_pid(result.hits[0].pid)


def get_all_documents_with_files():
    """Return all hits documents with files to be migrated."""
    search = DocumentSearch().filter(
        "bool",
        filter=[
            Q("term", _migration__eitems_has_files=True),
        ],
    )
    return search.execute()
