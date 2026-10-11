"""
Testovi za osint-ai-agent.
Pokruni: pytest -v
"""
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Postavi fake API key pre importa
os.environ["GEMINI_API_KEY"] = "test_key_12345"

# Dodaj root folder u path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Mock google.generativeai pre importa
with patch("google.generativeai.configure"):
    with patch("google.generativeai.GenerativeModel"):
        import agent


# ============================================================
# TESTIRANJE ip_lookup()
# ============================================================

class TestIpLookup:
    """Testovi za ip_lookup funkciju."""

    @patch("agent.requests.get")
    def test_successful_lookup(self, mock_get):
        """Testira uspešan IP lookup."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "city": "Belgrade",
            "country_name": "Serbia",
            "org": "Test ISP",
        }
        mock_get.return_value = mock_response

        result = agent.ip_lookup("8.8.8.8")
        assert "Belgrade" in result
        assert "Serbia" in result
        assert "Test ISP" in result

    @patch("agent.requests.get")
    def test_missing_fields(self, mock_get):
        """Testira nedostajuća polja."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = agent.ip_lookup("8.8.8.8")
        assert "?" in result

    @patch("agent.requests.get")
    def test_network_error(self, mock_get):
        """Testira mrežnu grešku."""
        mock_get.side_effect = Exception("Network error")
        result = agent.ip_lookup("8.8.8.8")
        assert "Greška" in result

    @patch("agent.requests.get")
    def test_timeout_parameter(self, mock_get):
        """Testira da je timeout postavljen."""
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        agent.ip_lookup("8.8.8.8")
        call_args = mock_get.call_args
        timeout = call_args.kwargs.get("timeout") or call_args[1].get("timeout")
        assert timeout == 10


# ============================================================
# TESTIRANJE exif_lookup()
# ============================================================

class TestExifLookup:
    """Testovi za exif_lookup funkciju."""

    @patch("agent.Image.open")
    def test_no_exif(self, mock_open):
        """Testira sliku bez EXIF-a."""
        mock_img = MagicMock()
        mock_img.getexif.return_value = {}
        mock_open.return_value.__enter__.return_value = mock_img

        result = agent.exif_lookup("test.jpg")
        assert "Nema EXIF" in result

    @patch("agent.Image.open")
    def test_with_exif(self, mock_open):
        """Testira sliku sa EXIF-om."""
        mock_img = MagicMock()
        mock_img.getexif.return_value = {
            271: "Test Camera",  # Make
            272: "Test Model",   # Model
        }
        mock_open.return_value.__enter__.return_value = mock_img

        result = agent.exif_lookup("test.jpg")
        assert "Make" in result or "Test Camera" in result

    @patch("agent.Image.open")
    def test_file_not_found(self, mock_open):
        """Testira nepostojeći fajl."""
        mock_open.side_effect = FileNotFoundError("File not found")
        result = agent.exif_lookup("nonexistent.jpg")
        assert "Greška" in result

    @patch("agent.Image.open")
    def test_skips_gps_info(self, mock_open):
        """Testira da se GPSInfo preskače."""
        mock_img = MagicMock()
        mock_img.getexif.return_value = {
            34853: "GPS data",  # GPSInfo tag
            271: "Make value",
        }
        mock_open.return_value.__enter__.return_value = mock_img

        result = agent.exif_lookup("test.jpg")
        assert "GPSInfo" not in result


# ============================================================
# TESTIRANJE ask_agent()
# ============================================================

class TestAskAgent:
    """Testovi za ask_agent funkciju."""

    def test_ask_agent_returns_response(self):
        """Testira da ask_agent vraća odgovor."""
        with patch.object(agent, "model") as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Test odgovor"
            mock_model.generate_content.return_value = mock_response

            result = agent.ask_agent("test pitanje")
            assert result == "Test odgovor"

    def test_ask_agent_contains_prompt(self):
        """Testira da prompt sadrži korisničko pitanje."""
        with patch.object(agent, "model") as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Odgovor"
            mock_model.generate_content.return_value = mock_response

            agent.ask_agent("Moje pitanje")
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert "Moje pitanje" in prompt

    def test_ask_agent_mentions_ip_command(self):
        """Testira da prompt pominje /ip komandu."""
        with patch.object(agent, "model") as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Odgovor"
            mock_model.generate_content.return_value = mock_response

            agent.ask_agent("test")
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert "/ip" in prompt

    def test_ask_agent_mentions_exif_command(self):
        """Testira da prompt pominje /exif komandu."""
        with patch.object(agent, "model") as mock_model:
            mock_response = MagicMock()
            mock_response.text = "Odgovor"
            mock_model.generate_content.return_value = mock_response

            agent.ask_agent("test")
            call_args = mock_model.generate_content.call_args
            prompt = call_args[0][0]
            assert "/exif" in prompt


# ============================================================
# TESTIRANJE API KEY
# ============================================================

class TestApiKey:
    """Testovi za API key konfiguraciju."""

    def test_api_key_from_env(self):
        """Testira da se API key čita iz env varijable."""
        # Postavljeno u setup-u
        assert os.getenv("GEMINI_API_KEY") == "test_key_12345"

    def test_api_key_not_hardcoded(self):
        """Testira da API key nije hardkodovan."""
        # Proveri da agent.py ne sadrži hardkodovan ključ
        agent_path = Path(__file__).resolve().parent.parent / "agent.py"
        content = agent_path.read_text(encoding="utf-8")
        assert "TVOJ_GEMINI_API_KEY_OVDE" not in content
