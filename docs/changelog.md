# Release Notes
---

## [0.3.1](https://github.com/hiperhealth/hiperhealth/compare/0.3.0...0.3.1) (2025-11-30)


### Bug Fixes

* Fix typo in error message for file processing ([#93](https://github.com/hiperhealth/hiperhealth/issues/93)) ([933b8d6](https://github.com/hiperhealth/hiperhealth/commit/933b8d6034789531b09c73277d4b459a2082ccfa))

# [0.3.0](https://github.com/hiperhealth/hiperhealth/compare/0.2.0...0.3.0) (2025-11-27)


### Bug Fixes

* Fix issues pointed by linter ([#80](https://github.com/hiperhealth/hiperhealth/issues/80)) ([70bacdd](https://github.com/hiperhealth/hiperhealth/commit/70bacdd144e4215f50bde2a0700fb9b0773b12c7))
* **research:** Resolve patient creation and submission errors ([#62](https://github.com/hiperhealth/hiperhealth/issues/62)) ([f0ea4ff](https://github.com/hiperhealth/hiperhealth/commit/f0ea4ff3ef758a47eafccd664a1157a5a186cc7f))


### Features

*  Add support for persisting data from each step ([#33](https://github.com/hiperhealth/hiperhealth/issues/33)) ([acdb8ee](https://github.com/hiperhealth/hiperhealth/commit/acdb8ee754b7b1030cfa2804e48422bf08c9f68a))
* Add tests for ResearchRepository and update dependencies ([#69](https://github.com/hiperhealth/hiperhealth/issues/69)) ([7e47ccc](https://github.com/hiperhealth/hiperhealth/commit/7e47ccc2e8c621b5ed1ec16330bd689c4715db86))
* added step to upload pdf/images test reports in the evaluation pipeline ([#38](https://github.com/hiperhealth/hiperhealth/issues/38)) ([327faf8](https://github.com/hiperhealth/hiperhealth/commit/327faf867c25d67ef9dfaea8875bae09cec744a2))
* **docs:** Add developer guide and integrate all-contributors ([#49](https://github.com/hiperhealth/hiperhealth/issues/49)) ([261c212](https://github.com/hiperhealth/hiperhealth/commit/261c212cde8f17205d58951956082e1061629f09))
* **research:** Migrate research app from JSON to SQL database ([#40](https://github.com/hiperhealth/hiperhealth/issues/40)) ([3cfd2a4](https://github.com/hiperhealth/hiperhealth/commit/3cfd2a4fe7d41c828a7342329c571c6e0786c15f))

# [0.2.0](https://github.com/hiperhealth/hiperhealth/compare/0.1.0...0.2.0) (2025-08-15)


### Bug Fixes

* Add missed clinical_outputs module ([#22](https://github.com/hiperhealth/hiperhealth/issues/22)) ([e29e791](https://github.com/hiperhealth/hiperhealth/commit/e29e791c5e3f471a646da6040720a5b4b6d54601))
* **ci:** Update dependencies and fix linter ([#4](https://github.com/hiperhealth/hiperhealth/issues/4)) ([c74a912](https://github.com/hiperhealth/hiperhealth/commit/c74a9126c21c819b6080f563a715d5ff84052701))
* Fix models generation ([#13](https://github.com/hiperhealth/hiperhealth/issues/13)) ([72a12ac](https://github.com/hiperhealth/hiperhealth/commit/72a12ac193901352f9084a87aa0e7e3b81e6da32))
* Fix packaging ([#7](https://github.com/hiperhealth/hiperhealth/issues/7)) ([6459f05](https://github.com/hiperhealth/hiperhealth/commit/6459f057eabae8619146078be92e826a2c7b993d))
* **release:** update version placeholder to use single quotes in __init__.py ([#5](https://github.com/hiperhealth/hiperhealth/issues/5)) ([6c71c07](https://github.com/hiperhealth/hiperhealth/commit/6c71c07e44231a3e98c831dda0c800eab8017099))


### Features

* Add a WEB App for the research ([#16](https://github.com/hiperhealth/hiperhealth/issues/16)) ([9502798](https://github.com/hiperhealth/hiperhealth/commit/950279821027b5d35c400dbed22369652b1c4180))
* Add dashboard ([#23](https://github.com/hiperhealth/hiperhealth/issues/23)) ([9c1e85b](https://github.com/hiperhealth/hiperhealth/commit/9c1e85be6337e18b4170564b1a8aee1e2470511e))
* add evaluation data capture to research app ([#28](https://github.com/hiperhealth/hiperhealth/issues/28)) ([f24a776](https://github.com/hiperhealth/hiperhealth/commit/f24a7762a98be91c8f4aea9ead60f85639e71d65))
* Add initial workflow for records, diagnostics, and treatment ([#12](https://github.com/hiperhealth/hiperhealth/issues/12)) ([28fab52](https://github.com/hiperhealth/hiperhealth/commit/28fab527641e8f4d6b2c942933fe654b321b80e6))
* allow user to add custom options/suggestions ([#29](https://github.com/hiperhealth/hiperhealth/issues/29)) ([1ac0376](https://github.com/hiperhealth/hiperhealth/commit/1ac0376a873a66b84e1ea3527eee6a8c0c25f3f1))
* FHIR extraction from images (jpeg, jpf, png), pdf from Diagnostic Reports. ([#27](https://github.com/hiperhealth/hiperhealth/issues/27)) ([7913d5e](https://github.com/hiperhealth/hiperhealth/commit/7913d5ec0cb83c6cada664e4c6f30bd33b24c3e1))
* **i18n:** add language selector and pass lang to AI helpers ([#18](https://github.com/hiperhealth/hiperhealth/issues/18)) ([f099ee3](https://github.com/hiperhealth/hiperhealth/commit/f099ee3a4e114d7e1a671a77aca53d5db661f00a))
* Improve the package structure ([#14](https://github.com/hiperhealth/hiperhealth/issues/14)) ([97c0029](https://github.com/hiperhealth/hiperhealth/commit/97c0029652f6253c648cd6e88708c98340a65f8d))
* Initial Implementation of hiperhealth module - medical_reports.py ([#6](https://github.com/hiperhealth/hiperhealth/issues/6)) ([5b02205](https://github.com/hiperhealth/hiperhealth/commit/5b02205d05812be881f3dea17b07601b638cecd9))
* **llm-output:** enforce JSON replies and log raw LLM output to `data/llm_raw/` ([#21](https://github.com/hiperhealth/hiperhealth/issues/21)) ([66e0872](https://github.com/hiperhealth/hiperhealth/commit/66e087273d63b01003699223be792b36bcd9b93c))
