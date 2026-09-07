# django-dynamic-fixture threat model

## Overview

A developer/test fixture library constructs Django model graphs from trusted model classes, field overrides, fixture algorithms and reusable lessons. new constructs instances (with optional persisted dependencies); get persists them and related objects. It uses the host ORM and file storage and is not a public data-ingestion service (django_dynamic_fixture/__init__.py:94; django_dynamic_fixture/__init__.py:125; django_dynamic_fixture/ddf.py:638).

Fixture generation is a privileged developer operation. The test environment, application settings and model save hooks determine the resources affected, including external effects of host-defined callbacks. The library does not automatically select a disposable database or provide rollback for an entire generated graph. new and get distinguish model persistence intent, but that distinction must not be expanded into a promise that no file or dependency operation occurs.

| Component | Source |
| --- | --- |
| Facade, model lookup and nested overrides | django_dynamic_fixture/__init__.py:32; django_dynamic_fixture/__init__.py:94 |
| Configuration and trusted fixture classes | django_dynamic_fixture/global_settings.py:32; django_dynamic_fixture/global_settings.py:54 |
| Model/file persistence and diagnostics | django_dynamic_fixture/ddf.py:449; django_dynamic_fixture/ddf.py:638 |
| Manual package publication guidance | setup.py:8 |

| Deployment or workflow | Resource or capability | Configuration and precedence | Safe effective value or location | Readers, writers, or recipients | Enforcing control | Evidence or unknowns |
| --- | --- | --- | --- | --- | --- | --- |
| Library embedded in Django | ORM save | Facade get/direct DynamicFixture.get → new with dependencies → optional full_clean → save + M2M | Caller model table/database routing and recursively generated dependencies | Host DB, signals and custom save receivers | Caller DB privileges and isolation; optional full_clean | django_dynamic_fixture/ddf.py:627; django_dynamic_fixture/ddf.py:638 |
| Library embedded in Django | File fixture materialization | Field override → Django File → optional underlying path reopen → field.save(name, file, save=False) | FileField storage-generated name from supplied Django File.name; existing local File path may be reopened | Configured storage backend and file readers | Django storage implementation and caller file access | django_dynamic_fixture/ddf.py:449 |
| Library embedded in Django | Diagnostics | Facade debug_mode/print_errors options and settings → debug logging or error print_field_values | Configured Python logger in debug mode; console field values on error when print_errors enabled | Host log/console collectors | Caller debug/print_errors selection | django_dynamic_fixture/ddf.py:466; django_dynamic_fixture/ddf.py:662 |
| Facade new versus direct DynamicFixture.new | Dependency construction | Facade explicit/default persist_dependencies=False; direct method default=True; get uses direct default | Facade default: unsaved dependency models; direct default/get: generated dependencies may persist through host ORM | Host database and model signal/save-hook recipients when persistence enabled | Caller API/flag selection and host DB authority; FileField writes are separate | django_dynamic_fixture/__init__.py:94; django_dynamic_fixture/ddf.py:523; django_dynamic_fixture/ddf.py:644 |

## Threat Model, Trust Boundaries, and Assumptions

**Protected assets.** Host database records, relation graphs and files created by fixtures (django_dynamic_fixture/ddf.py:655; django_dynamic_fixture/ddf.py:461). Supplied field data exposed through optional debug output and error diagnostics; callbacks and fixture configuration execute with host authority (django_dynamic_fixture/ddf.py:466; django_dynamic_fixture/ddf.py:662).

**Actors and starting authority.** A user only influences fixture behavior if a host exposes these developer APIs; no public endpoint is established. A test author with model/config/callback access already has broad host application authority, including side effects of model save hooks.

**Trust boundaries and owned controls.**

- Facade resolves supplied model strings through apps.get_model and expands nested field aliases; callers choose n and graph configuration. This is developer authority, not a safe authorization boundary for arbitrary end-user model names (django_dynamic_fixture/__init__.py:32; django_dynamic_fixture/__init__.py:113).
- Most DDF configuration resolves environment, then Django settings, then defaults. Default fixture class selection specifically reads Django settings and may import a custom class. Trusted plugins/callbacks execute inside the application process (django_dynamic_fixture/global_settings.py:32; django_dynamic_fixture/global_settings.py:54; django_dynamic_fixture/ddf.py:650).
- get optionally invokes full_clean, then model.save and callbacks, followed by M2M handling. Validation is off by default and does not authorize writes; failure/transaction isolation belongs to the caller test harness (django_dynamic_fixture/global_settings.py:87; django_dynamic_fixture/ddf.py:647).
- A supplied Django File can reopen its underlying path and save through the model field storage even while preparing field data. A nonpersisted model object therefore is not a guarantee of no file-storage writes (django_dynamic_fixture/ddf.py:449).
- Facade new uses persist_dependencies=False by default, whereas direct DynamicFixture.new defaults it to True; get calls the latter without overriding that default. Direct and facade callers therefore have materially different dependency-write behavior (django_dynamic_fixture/__init__.py:94; django_dynamic_fixture/ddf.py:523; django_dynamic_fixture/ddf.py:644).

**Security objectives.** Run fixtures against intentionally selected disposable or authorized databases and storage. Keep arbitrary model/field/callback configuration away from untrusted request input. Prevent debug/error diagnostics from leaking real sensitive fixture data; bound graph/count work in the invoking harness.

**Assumptions and unresolved controls.**

- Default fill_nullable_fields is false in settings despite facade parameter documentation saying true; effective settings consumer wins (django_dynamic_fixture/global_settings.py:86; django_dynamic_fixture/__init__.py:105).
- Host DB alias, storage backend and atomicity are not specified here; package provides no separate sandbox.
- Setup comments describe manual package upload; publisher credentials and current release procedure are not present (setup.py:8).
- Exact fixture resources, storage permissions, host callback effects and transaction cleanup are unknown. For supported operational use, the invoker must separately establish target authorization; the library’s test-oriented purpose is not an isolation mechanism.

## Attack Surface, Mitigations, and Attacker Stories

These are prioritized hypotheses, not validated vulnerabilities. Each requires its stated caller, data and exposure prerequisites; ordinary use of authority already granted is not a new capability.

| Priority | Scenario and capability gain | Prerequisites | Impact | Existing controls | Mitigation | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A supposedly disposable fixture run writes to a real database or storage backend. | The invoker configures live resources or reuses host settings with write authority. | Unintended model/file creation or modification and side effects of host save hooks. | Explicit API distinction, caller model configuration and existing database/storage access controls. | Select isolated resources explicitly and bind operational authorization to the actual target. | django_dynamic_fixture/__init__.py:94; django_dynamic_fixture/ddf.py:655; django_dynamic_fixture/ddf.py:461 |
| 2 | A host exposes arbitrary model names, field overrides, counts or fixture callbacks to a lower-trust user. | A real integration wraps developer fixture APIs in a request/automation interface. | Unauthorized object/relationship creation, excessive graph work or host-code authority. | apps.get_model and field-name validation; no independent user-permission model. | Restrict any wrapper to approved models/fields and bounded counts; keep callables trusted. | django_dynamic_fixture/__init__.py:113; django_dynamic_fixture/__init__.py:149; django_dynamic_fixture/ddf.py:480 |
| 2 | Sensitive supplied fixture data reaches console/log readers after a generation failure or debug output. | Fixtures contain real sensitive values and log readers lack corresponding data access. | Confidentiality loss through diagnostic copies. | Debug mode defaults false; print_errors and configured logging are caller options. | Use synthetic data and disable/minimize sensitive error output. | django_dynamic_fixture/global_settings.py:88; django_dynamic_fixture/ddf.py:466; django_dynamic_fixture/ddf.py:662 |
| 3 | A caller assumes new means no writes or get means fully validated/atomic graph creation. | A real workflow depends on FileField side effects, disabled full_clean or partial failure across saves/relations. | Unexpected persistent artifacts or inconsistent test/operational state. | Documented persistence options; optional model validation; Django storage and model hooks. | Treat storage separately and use a suitable caller transaction/cleanup boundary. | django_dynamic_fixture/ddf.py:449; django_dynamic_fixture/ddf.py:647; django_dynamic_fixture/ddf.py:667 |

## Severity Calibration (Critical, High, Medium, Low)

| Level | Repository-specific example | Counterexample or limiting prerequisite |
| --- | --- | --- |
| Critical | An exposed host wrapper grants broad privileged model/code access across a verified lower-trust boundary. | No such wrapper exists here; a trusted test author using arbitrary models has existing authority. |
| High | A real misbound fixture operation corrupts sensitive live data or exposes substantial confidential diagnostics. | Requires live-resource authority and material affected data, not ordinary disposable test writes. |
| Medium | A bounded authorized workflow leaves inconsistent records/files after partial failure or leaks limited sensitive values. | Caller-managed transactions, isolated storage and synthetic data can remove the stated impact. |
| Low | A local fixture build fails or generates unsuitable synthetic data without shared-resource consequences. | Manual package upload comments and trusted callback execution are not findings by themselves. |

This model uses an independent source-backed architecture pass. Repository citations were checked against the supplied inventory and source lines; application code and external services were not executed. Source-established behavior is distinct from unverified deployment exposure. Revisit the model when the described input, storage, authorization or publication boundaries change.

Repository: github.com/mathspace/django-dynamic-fixture
Version: fae2e3dc009a1e7eb3017b51fbb6e295cda174fc
