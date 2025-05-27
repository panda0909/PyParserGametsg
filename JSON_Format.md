- **item_id**: 字串，物品的唯一識別碼，如 `"2"`、`"70"`、`"2779"` 等。

- **item_name**: 字串，物品的名稱，如 `"風刃短劍"`、`"歐西斯短劍"` 等。

- **item_url**: 字串，物品在遊戲資料庫網站的 URL，例如 `https://www.gametsg.net/equip/detail.html?id=2`。

- **item_image**: 字串，物品圖片的 URL。

- **item_classes**: 陣列，可使用此物品的職業列表，每個元素包含：
    - **name**: 字串，職業名稱，如 `"騎士"`、`"妖精"` 等。
    - **level**: 字串，職業等級要求，如 `"level01"`、`"level02"` 等。

- **attack**: 字串，武器的攻擊力，如 `"25 / 16"`、`"8/9"` 等，或者 `"-"` 表示無等級要求。

- **defense**: 字串，物理防禦力(AC)，如 `"-8"`、`"0"`。

- **item_stats**: 陣列，包含物品的屬性字串列表。

- **item_stats2**: 陣列，包含物品的祝福屬性。

- **weight**: 重量。

- **mertrial**: 材質。

- **canbedmg**: 損傷，如 `"不會被損壞"`。

- **store**: 倉庫，如 `"可存倉"`。

- **trade**: 交換，如 `"可交易"`。

- **safe_val**: 安定值，如 `"安全強化至6"`。

- **data_zhiye**: 字串，使用「|」分隔的職業 ID 列表，如 `"1|8"`、`"14"` 等。

- **category_id**: 字串，物品類別 ID，如 `"2"`、`"48"` 等。

- **category_name**: 字串，物品類別名稱，如 `"匕首"`、`"符石劍"` 等。

- **monster_drops**: 陣列（可選），哪些怪物會掉落此物品，每個元素包含：
    - **monster_name**: 字串，怪物名稱。
    - **monster_url**: 字串，怪物在遊戲資料庫網站的 URL。
    - **monster_id**: 字串，怪物 ID。
    - **monster_type**: 字串，怪物類型，如 `"monType01"`、`"monType02"` 等。
    - **monster_size**: 字串，怪物大小，如 `"小型"`、`"大型"` 等。
    - **monster_size_class**: 字串，怪物大小的 CSS 類別，如 `"size100"`、`"size200"` 等。
    - **monster_level**: 字串，怪物等級。
    - **monster_weaknesses**: 陣列，怪物的弱點屬性，每個元素包含：
        - **type**: 字串，弱點屬性類型，如 `"火"`、`"水"` 等。
        - **class**: 字串，弱點屬性的 CSS 類別，如 `"point01"`、`"point02"` 等。
        - **monster_areas**: 陣列，怪物出現的地區列表。