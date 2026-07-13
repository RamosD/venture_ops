"""Testes do adaptador de armazenamento filesystem (sem base de dados)."""
import hashlib
import tempfile
from pathlib import Path

from django.test import SimpleTestCase
from django.urls import Resolver404, resolve

from apps.storage.exceptions import (
    InvalidKeyError,
    ObjectNotFoundError,
    ObjectTooLargeError,
)
from apps.storage.filesystem import FilesystemStorageAdapter


class FilesystemStorageTests(SimpleTestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.storage = FilesystemStorageAdapter(root=self.root, max_bytes=1024)

    def test_save_and_open_roundtrip(self):
        content = "olá mundo — VentureOps".encode("utf-8")
        obj = self.storage.save(content)
        self.assertTrue(self.storage.exists(obj.key))
        self.assertEqual(self.storage.open(obj.key), content)
        self.assertEqual(obj.size, len(content))

    def test_key_is_server_generated_with_expected_shape(self):
        obj = self.storage.save(b"x")
        self.assertRegex(obj.key, r"^[0-9a-f]{2}/[0-9a-f]{30}$")

    def test_checksum_is_stable_and_sha256(self):
        content = b"conteudo estavel"
        obj = self.storage.save(content)
        self.assertEqual(obj.checksum, hashlib.sha256(content).hexdigest())
        # recalcular a partir do ficheiro devolve o mesmo valor (estável)
        self.assertEqual(self.storage.checksum(obj.key), obj.checksum)

    def test_path_traversal_is_rejected(self):
        for bad_key in [
            "../secret",
            "../../etc/passwd",
            "/etc/passwd",
            "ab/../../x",
            "..%2f..%2fx",
            "foo",
            "AB/" + "0" * 30,  # maiúsculas não permitidas
        ]:
            with self.assertRaises(InvalidKeyError):
                self.storage.open(bad_key)

    def test_open_missing_object_raises(self):
        with self.assertRaises(ObjectNotFoundError):
            self.storage.open("ab/" + "0" * 30)  # chave válida, inexistente

    def test_delete_removes_object(self):
        obj = self.storage.save(b"apagar")
        self.assertTrue(self.storage.exists(obj.key))
        self.storage.delete(obj.key)
        self.assertFalse(self.storage.exists(obj.key))

    def test_size_limit_enforced(self):
        with self.assertRaises(ObjectTooLargeError):
            self.storage.save(b"x" * 2048)

    def test_object_is_stored_inside_private_root(self):
        obj = self.storage.save(b"privado")
        stored = (self.root / obj.key).resolve()
        self.assertTrue(stored.is_file())
        self.assertTrue(str(stored).startswith(str(self.root.resolve())))


class StorageIsNotPubliclyRoutedTests(SimpleTestCase):
    def test_no_url_serves_storage_objects(self):
        for path in ["/storage/ab/x", "/media/ab/x", "/static/ab/x"]:
            with self.assertRaises(Resolver404):
                resolve(path)
