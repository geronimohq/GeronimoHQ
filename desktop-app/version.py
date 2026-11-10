"""
CS2 Command Center - Single Source of Truth for Application Versioning.
Imported across header, diagnostics, settings dialog, and build manifests.
"""

APP_VERSION = "2.0.2"
BUILD_DATE = "2026-11-11"

def get_app_version() -> str:
    return APP_VERSION

def get_build_date() -> str:
    return BUILD_DATE
