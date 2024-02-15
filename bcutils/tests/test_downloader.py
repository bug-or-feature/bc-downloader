import os
import pytest

from bcutils.bc_utils import (
    Resolution,
    get_barchart_downloads,
    create_bc_session,
    save_prices_for_contract,
    HistoricalDataResult,
    _build_save_path,
    _get_contract_month_year,
    _get_start_end_dates,
)


@pytest.fixture(autouse=True)
def download_dir(tmp_path):
    download_dir = tmp_path / "prices"
    download_dir.mkdir()
    return download_dir.absolute()


@pytest.fixture()
def bc_config():
    config = {
        "barchart_username": "BARCHART_USERNAME",
        "barchart_password": "BARCHART_PASSWORD",
    }
    bc_config = {k: os.environ.get(v) for k, v in config.items() if v in os.environ}
    return bc_config


class TestDownloader:
    def test_no_credentials(self, download_dir):
        with pytest.raises(Exception):
            get_barchart_downloads(
                create_bc_session(config_obj={}),
                contract_map={
                    "AUD": {"code": "A6", "cycle": "HMUZ", "tick_date": "2009-11-24"}
                },
                save_dir=download_dir,
                start_year=2020,
                end_year=2022,
                dry_run=False,
            )

    def test_bad_credentials(self, download_dir):
        with pytest.raises(Exception):
            get_barchart_downloads(
                create_bc_session(
                    config_obj=dict(
                        barchart_username="user@domain.com",
                        barchart_password="s3cr3t_321",
                    )
                ),
                contract_map={
                    "AUD": {"code": "A6", "cycle": "HMUZ", "tick_date": "2009-11-24"}
                },
                save_dir=download_dir,
                start_year=2020,
                end_year=2022,
                dry_run=False,
            )

    def test_hourly(self, bc_config, download_dir):
        if len(bc_config) == 0:
            pytest.skip("Skipping test, no Barchart credentials found in env")
        else:
            get_barchart_downloads(
                create_bc_session(config_obj=bc_config),
                contract_map={
                    "AUD": {"code": "A6", "cycle": "H", "tick_date": "2009-11-24"}
                },
                save_dir=download_dir,
                start_year=2020,
                end_year=2021,
                dry_run=False,
                pause_between_downloads=False,
            )

            csv = download_dir / "Hour_AUD_20200300.csv"
            assert csv.exists()
            assert not csv.is_dir()

    def test_daily(self, bc_config, download_dir):
        if len(bc_config) == 0:
            pytest.skip("Skipping test, no Barchart credentials found in env")
        else:
            get_barchart_downloads(
                create_bc_session(config_obj=bc_config),
                contract_map={
                    "AUD": {"code": "A6", "cycle": "H", "tick_date": "2009-11-24"}
                },
                save_dir=download_dir,
                start_year=2020,
                end_year=2021,
                do_daily=True,
                dry_run=False,
                pause_between_downloads=False,
            )

            csv = download_dir / "Day_AUD_20200300.csv"
            assert csv.exists()
            assert not csv.is_dir()

    def test_insufficient(self, bc_config, download_dir):
        if len(bc_config) == 0:
            pytest.skip("Skipping test, no Barchart credentials found in env")
        else:
            contract_key = "UPU14"
            month, year = _get_contract_month_year(contract_key)
            save_path = _build_save_path(
                "CHFJPY", month, year, Resolution.Hour, os.getcwd()
            )
            start_date, end_date = _get_start_end_dates(month, year)

            result = save_prices_for_contract(
                create_bc_session(config_obj=bc_config, do_login=False),
                contract_key,
                save_path,
                start_date,
                end_date,
            )

            assert result == HistoricalDataResult.INSUFFICIENT
