from application.db.models import OrganisationOrm, ProvisionQualityOrm
from application.data_access.digital_land_queries import get_providers_for_dataset


def add_provision_quality(
    db_session,
    dataset="greenspace",
    organisation="local-authority:X",
    organisation_name="Test Council",
    is_designated_provider=True,
    quality="authoritative",
    has_active_endpoint=True,
):
    db_session.add(
        ProvisionQualityOrm(
            dataset=dataset,
            organisation=organisation,
            organisation_name=organisation_name,
            has_active_endpoint=has_active_endpoint,
            has_active_resource=True,
            owns_entities=True,
            is_designated_provider=is_designated_provider,
            quality=quality,
            entity_count=10,
            quality_score=None,
        )
    )


class TestGetProvidersForDataset:
    def test_returns_empty_list_when_no_providers(self, db_session):
        result = get_providers_for_dataset(db_session, "greenspace")
        assert result == []

    def test_returns_provider_with_entity_from_organisation_table(self, db_session):
        db_session.add(
            OrganisationOrm(
                organisation="local-authority:X", name="Test Council", entity=100
            )
        )
        add_provision_quality(db_session)
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        assert len(result) == 1
        provider = result[0]
        assert provider.organisation == "local-authority:X"
        assert provider.organisation_name == "Test Council"
        assert provider.entity == 100
        assert provider.is_designated_provider is True

    def test_returns_none_entity_when_no_matching_organisation(self, db_session):
        add_provision_quality(
            db_session, organisation="unknown:Y", organisation_name="Unknown Org"
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        assert len(result) == 1
        assert result[0].entity is None

    def test_only_returns_providers_for_requested_dataset(self, db_session):
        add_provision_quality(db_session, dataset="greenspace")
        add_provision_quality(
            db_session, dataset="forest", organisation="local-authority:Z"
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "forest")

        assert len(result) == 1
        assert result[0].dataset == "forest"

    def test_distinguishes_authoritative_and_alternative_providers(self, db_session):
        add_provision_quality(
            db_session,
            organisation="local-authority:A",
            organisation_name="Authoritative Council",
            is_designated_provider=True,
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:B",
            organisation_name="Alternative Council",
            is_designated_provider=False,
            quality="some",
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        authoritative = [p for p in result if p.is_designated_provider]
        alternative = [p for p in result if not p.is_designated_provider]
        assert len(authoritative) == 1
        assert authoritative[0].organisation_name == "Authoritative Council"
        assert len(alternative) == 1
        assert alternative[0].organisation_name == "Alternative Council"

    def test_falls_back_to_organisation_table_name_when_provision_quality_name_is_null(
        self, db_session
    ):
        db_session.add(
            OrganisationOrm(
                organisation="local-authority:X", name="Test Council", entity=100
            )
        )
        add_provision_quality(db_session, organisation_name=None)
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        assert len(result) == 1
        assert result[0].organisation_name == "Test Council"

    def test_skips_provider_when_no_name_available_from_either_source(self, db_session):
        add_provision_quality(
            db_session, organisation="unknown:Y", organisation_name=None
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        assert result == []

    def test_excludes_provider_with_no_active_endpoint(self, db_session):
        add_provision_quality(
            db_session,
            organisation="local-authority:A",
            organisation_name="Decommissioned Council",
            has_active_endpoint=False,
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:B",
            organisation_name="Active Council",
            has_active_endpoint=True,
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        names = [p.organisation_name for p in result]
        assert names == ["Active Council"]

    def test_does_not_error_when_provider_has_no_name(self, db_session):
        add_provision_quality(
            db_session,
            organisation="local-authority:A",
            organisation_name="Zebra Council",
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:B",
            organisation_name=None,
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:C",
            organisation_name="Aardvark Council",
        )
        db_session.flush()

        result = get_providers_for_dataset(db_session, "greenspace")

        names = [p.organisation_name for p in result]
        assert names == ["Aardvark Council", "Zebra Council"]
