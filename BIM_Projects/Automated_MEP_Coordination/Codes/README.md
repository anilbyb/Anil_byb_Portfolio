# MEP Code and Data Index

See the [project README](../README.md) for Python inputs, execution state and limitations.

| Material | Repository entry |
| --- | --- |
| Domestic water data and Grasshopper definition | [02-DOW](02-DOW/) |
| Wastewater datasets | [03-WWS](03-WWS/) |
| RWS datasets | [04-RWS](04-RWS/) |
| Ventilation datasets and Grasshopper definition | [07-ven](07-ven/) |
| Additional top-level definitions | [get_DOW_data.gh](get_DOW_data.gh), [get_WWS_data.gh](get_WWS_data.gh) |
| AutoCAD helper | [get_layer_lines.lsp](02-DOW/get_layer_lines.lsp) |

The top-level `get_DOW_data.gh` and `02-DOW/get_DOW_data.gh` have identical Git blob hashes in the reviewed revision; both are preserved.

The four Python scripts documented in the project README, together with `get_DOW_data.gh`, `get_WWS_data.gh` and `07-ven/get_VentDuct_data_v03-LB1.gh`, were developed for the hospital project and subsequently reused on other projects. Directory names identify system groupings rather than separate projects. CSV presence does not guarantee that every script's hard-coded input path, schema or required model context is satisfied. Grasshopper definitions have not been executed in this review.

[Back to the project](../README.md)
