import logging

import requests

from anki_chinese_cards.utils import WindowsPath


class AnkiConnect:
    def __init__(
        self,
        anki_file_dir: WindowsPath,
        deck: str,
        url: str = "http://localhost:8765",
    ):
        """
        Args:
            url (str): the AnkiConnect server
            anki_file_dir (WindowsPath): path to the folder where Anki stores files
            deck (str): name of the Anki deck where notes are located
        """
        self.url = url
        self.anki_file_dir = anki_file_dir
        self.deck = deck

    def _request(self, action: str, params={}):
        """Send a request to AnkiConnect"""

        payload = {"action": action, "version": 6, "params": params}

        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Anki: {e}")
            return None

    def create_note(self, note: dict) -> int | None:
        """Creates a note. Returns the Note ID"""
        result = self._request("addNote", {"note": note})

        if result and result.get("result"):
            note_id = result["result"]
            deck = note["deckName"]
            logging.debug(f"Successfully added note: {note_id} in deck {deck}")
            return note_id
        else:
            if result and "error" in result:
                logging.error(f"Error adding note: {result['error']}")
            else:
                logging.error("Unknown error adding note")
            return None

    def delete_note(self, note_id: int):
        """Delete note"""
        result = self._request("deleteNotes", {"notes": [note_id]})

        if result and result.get("error") is None:
            logging.info(f"Successfully deleted note: '{note_id}'")
            return result["result"]
        else:
            if result and "error" in result:
                logging.error(f"Error deleting note: {result['error']}")
            else:
                logging.error("Unknown error deleting note")
            return None

    def _get_notes(self, query: str="") -> list[dict]:
        """Returns list of notes that match query"""
        result = self._request("notesInfo", {"query": f'"deck:{self.deck}" {query}'})
        return result.get("result", []) if result else []

    def _get_note_ids(self, query: str="") -> list[int]:
        """Returns list of note IDs that match query"""
        result = self._request("findNotes", {"query": f'"deck:{self.deck}" {query}'})
        return result.get("result", []) if result else []

    def _get_note_by_id(self, note_id: int):
        """Get note by ID"""
        result = self._request("notesInfo", {"notes": [note_id]})
        if result and len(result.get("result", [])) > 0:
            return result["result"][0]
        return None

    def _append_to_note_field(self, note_id: int, field_name: str, value: str):
        """Appends `value` to note `field_name` value."""
        note = self._get_note_by_id(note_id)
        if note is None:
            logging.error(f"Could not find note with id {note_id}")
            return

        new_value = note["fields"][field_name]["value"]
        if new_value:
            new_value += "<br>"
        new_value += value

        self._update_note_field(note_id, field_name, new_value)

    def _update_note_field(self, note_id: int, field_name: str, field_value: str):
        """Update field value"""
        result = self._request(
            "updateNote",
            {"note": {"id": note_id, "fields": {f"{field_name}": field_value}}},
        )
        if result and result.get("result"):
            logging.info(
                f"Successfully updated field {field_name} in note {note_id} to new value"
            )

    def create_deck(self):
        """Create a new deck"""
        result = self._request("createDeck", {"deck": self.deck})
        return result and result.get("result")

    def delete_deck(self):
        """Delete deck"""
        result = self._request("deleteDecks", {"decks": [self.deck], "cardsToo": True})
        return result and result.get("result")
