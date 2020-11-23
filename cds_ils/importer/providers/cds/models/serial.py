# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# CDS-ILS is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.

"""CDS-ILS Serial model."""

from __future__ import unicode_literals

from cds_ils.importer.overdo import CdsIlsOverdo
from cds_ils.importer.providers.cds.ignore_fields import CDS_IGNORE_FIELDS


class CDSSerial(CdsIlsOverdo):
    """Translation Index for CDS Books."""

    __model_ignore_keys__ = {
        "020__a",
        "020__b",
        "020__c",
        "020__u",
        "022__a",
        "022__b",
        "0247_2",
        "0247_9",
        "0247_a",
        "0247_q",
        "0247_y",
        "0248_q",
        "035__9",
        "035__a",
        "035__d",
        "035__h",
        "035__m",
        "035__t",
        "035__u",
        "035_a9",
        "035_aa",
        "037__9",
        "037__a",
        "037__c",
        "041__a",
        "044__a",
        "050_4a",
        "050__a",
        "080__a",
        "082042",
        "08204a",
        "082__a",
        "084__2",
        "084__a",
        "088__9",
        "088__a",
        "100__a",
        "100__e",
        "100__u",
        "100__9",
        "110__a",
        "111__9",
        "111__a",
        "111__c",
        "111__g",
        "111__n",
        "111__w",
        "111__y",
        "111__z",
        "210__a",
        "222__a",
        "242__a",
        "245__9",
        "245__a",
        "245__b",
        "245__c",
        "246__a",
        "246__i",
        "246__n",
        "246__p",
        "250__a",
        "260__a",
        "260__b",
        "260__c",
        "270__a",
        "270__d",
        "270__k",
        "270__l",
        "270__m",
        "300__a",
        "300__b",
        "310__a",
        "4901_a",
        "490__v",
        "500__9",
        "500__a",
        "5050_a",
        "505__a",
        "505__t",
        "520__9",
        "520__a",
        "536__a",
        "536__c",
        "536__f",
        "536__r",
        "540__3",
        "540__a",
        "540__u",
        "541__9",
        "542__3",
        "542__d",
        "542__g",
        "583__c",
        "595__9",
        "595__a",
        "595__i",
        "595__z",
        "65027b",
        "6531_9",
        "6531_a",
        "690C_a",
        "690c_a",
        "693__a",
        "693__e",
        "695__9",
        "695__a",
        "697C_a",
        "700__0",
        "700__9",
        "700__a",
        "700__e",
        "700__i",
        "700__u",
        "710__5",
        "710__a",
        "710__e",
        "710__g",
        "711__9",
        "711__a",
        "711__c",
        "711__d",
        "711__f",
        "711__g",
        "711__n",
        "711__w",
        "711__z",
        "773__c",
        "773__n",
        "773__p",
        "773__v",
        "773__w",
        "773__y",
        "773__y",
        "775__a",
        "775__b",
        "775__c",
        "775__w",
        "852__p",
        "8564_8",
        "8564_s",
        "8564_t",
        "8564_u",
        "8564_w",
        "8564_x",
        "8564_y",
        "859__f",
        "901__u",
        "912__f",
        "912__r",
        "916__a",
        "916__s",
        "916__w",
        "933__a",
        "933__b",
        "938__a",
        "938__p",
        "960__a",
        "962__k",
        "970__a",
        "970__d",
        "980__a",
        "980__b",
        "980__c",
        "993__r",
        "999C6a",
    }

    __query__ = (
        '003:SzGeCERN AND (690C_:BOOK OR 690C_:"YELLOW REPORT" OR '
        "980__:PROCEEDINGS OR "
        "697C_:LEGSERLIB -980__:DELETED -980__:MIGRATED)"
        " AND 490__:/[a-zA-Z0-9]+/"
    )

    __ignore_keys__ = CDS_IGNORE_FIELDS | __model_ignore_keys__

    _default_fields = {
        "_migration": {"record_type": "serial", "children": []},
        "mode_of_issuance": "SERIAL",
    }


model = CDSSerial(bases=(), entry_point_group="cds_ils.importer.series")
