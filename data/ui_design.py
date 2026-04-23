import logging
log = logging.getLogger(__name__)

from ui_config import UI, Text, Image, ui_manager
from visual_config import COLORS, FONTS, SQUARE_SIZE, frame_mid_rect, frame_lo_rect, frame_hi_rect, s, frame_hi_h, \
    frame_border, std_padding, std_dist
from world_config import format_time_short

#permanent UI elements------------------------------------------------------------------

ui_permanent_borders = UI(
    name = "permanent_borders",
    pos = (frame_mid_rect[0] - frame_border, frame_mid_rect[1]),
    size = (frame_mid_rect[2] + frame_border * 2, frame_mid_rect[3]),
    fill = COLORS["transparent"],
    border = COLORS["yellow_border"],
    layer = 33,
    visible = True
)

ui_time_bar = UI(
    name = "time_bar",
    pos = frame_hi_rect[:2],
    size = frame_hi_rect[2:],
    fill = COLORS["black"],
    text = [
        Text(
            text = "time",
            font = FONTS["topaz_m"],
            color = COLORS["white"]
      )
    ],
    layer = 33,
    visible = False
)

ui_home_bar = UI(
    name = "home_bar",
    pos = frame_lo_rect[:2],
    size = frame_lo_rect[2:],
    fill = COLORS["black"],
    layer = 33,
    visible = True
)

ui_back_button = UI(
    name = "back_button",
    pos = (s(25), frame_lo_rect[1] + frame_lo_rect[3] / 2 - s(25)),
    size = (s(100), s(50)),
    fill = COLORS["yellow_lo"],
    function = lambda: ui_manager.menu_back(),
    text = [
        Text(
            text = "<<<",
            font = FONTS["topaz_l"],
            v_align = "top",
            pad_x = s(6),
            pad_y = s(10),
        )
    ],
    layer = 33,
    visible = True
)

#start menu UI elements------------------------------------------------------------

ui_start_title = UI(
    name = "start_title",
    pos = (std_padding * 2, frame_hi_h + std_padding * 3),
    size = (SQUARE_SIZE - std_padding * 4, s(120)),
    fill = COLORS["transparent"],
    border = COLORS["yellow_border"],
    layer = 1,
    text = [
        Text(
            text = "PRODUKTIV",
            font = FONTS["topaz_xxl"]
        )
    ],
)

ui_start_continue = UI(
    name = "start_continue",
    pos = (std_padding * 3, ui_start_title.pos[1] + std_dist + std_padding * 3),
    size = (ui_start_title.size[0] - std_padding * 2, s(70)),
    fill = COLORS["yellow_lo"],
    layer = 1,
    function = lambda: ui_manager.continue_game(),
    text = [
        Text(
            text = "Continue",
            font = FONTS["topaz_l"],
            color = COLORS["black"]
        )
    ],
)

ui_start_saves = UI(
    name = "start_saves",
    pos = (ui_start_continue.pos[0], ui_start_continue.pos[1] + std_dist),
    size = ui_start_continue.size,
    fill = COLORS["yellow_mid"],
    layer = 1,
    function = lambda: ui_manager.menu_switch("saves"),
    text = [
        Text(
            text = "Save menu",
            font = FONTS["topaz_l"]
        )
    ],
)

ui_start_new_game = UI(
    name = "start_new_game",
    pos = (ui_start_saves.pos[0], ui_start_saves.pos[1] + std_dist),
    size = ui_start_continue.size,
    fill = COLORS["yellow_mid"],
    layer = 1,
    function = lambda: ui_manager.new_game(),
    text = [
        Text(
            text = "New game",
            font = FONTS["topaz_l"]
        )
    ],
)

#saves menu UI elements--------------------------------------------------------

ui_saves_bg = UI(
    name = "saves_bg",
    pos = frame_mid_rect[:2],
    size = frame_mid_rect[2:],
    fill = COLORS["blue_lo"],
    layer = 0
)

ui_saves_header = UI(
    name = "saves_header",
    pos = (std_padding, frame_hi_h + std_padding),
    size = (SQUARE_SIZE - std_padding * 2, s(60)),
    fill = COLORS["blue_mid"],
    layer = 1,
    text = [
        Text(
            text = "Saves:",
            h_align = "left",
            font = FONTS["topaz_l"]
        )
    ],
)

ui_saves_new_save_button = UI(
    name = "saves_new_save_button",
    pos = (SQUARE_SIZE - std_padding * 6 - ui_back_button.size[0],
           ui_saves_header.pos[1] + std_padding // 4.4),
    size = (ui_back_button.size[0] + std_padding * 4, ui_back_button.size[1]),
    fill = COLORS["blue_hi"],
    layer = 2,
    text = [
        Text(
            text = "New",
            font = FONTS["topaz_l"]
        )
    ]
)

for i in range(5):
    UI(
        name = f"saves_grid_cell_{i+1}",
        pos = (std_padding * 2,
               ui_saves_header.pos[1] + ui_saves_header.size[1] +
               std_padding + i * (s(70) + std_padding)),
        size = (s(624), s(70)),
        fill = COLORS["blue_lo"],
        layer = 1
    )

#new save UI elements------------------------------------------------

ui_new_save_bg = UI(
    name = "new_save_bg",
    pos = ui_saves_bg.pos,
    size = ui_saves_bg.size,
    fill = COLORS["cyan_lo"],
    layer = 0
)

ui_new_save_box = UI(
    name = "new_save_box",
    pos = (std_padding * 3, SQUARE_SIZE // 3),
    size = (SQUARE_SIZE - std_padding * 6, s(120)),
    fill = COLORS["cyan_mid"],
    layer = 1,
    text = [
        Text(
        text = "Save name:",
        font = FONTS["topaz_m"],
        h_align = "left",
        v_align = "top",
        pad_x = s(12),
        pad_y = s(12),
        )
    ]
)

ui_new_save_input_box = UI(
    name = "new_save_input_box",
    pos = (std_padding * 3 + s(12), ui_new_save_box.pos[1] + std_padding + s(12)),
    size = (s(555), s(70)),
    fill = COLORS["cyan_lo"],
    layer = 2,
    text = [
        Text(
            text = "",
            font = FONTS["topaz_m"],
            h_align = "left"
        )
    ]
)

ui_new_save_button = UI(
    name = "new_save_button",
    pos = (std_padding * 8, ui_new_save_input_box.pos[1] + s(100)),
    size = (s(324), s(100)),
    fill = COLORS["cyan_mid"],
    layer = 1,
    text = [
        Text(
            text = "Save",
            font = FONTS["topaz_xl"],
        )
    ]
)



#main menu UI elements-----------------------------------------------

image_size = s(210)

icon_scale = 1.75

pfp_scale = 2.5

img_scale = 3.225

cover_scale = 3.5

ui_main_facilities = UI(
    name = "main_facilities",
    pos = (std_padding, frame_mid_rect[1] + std_padding),
    size = (SQUARE_SIZE // 2 - std_padding * 1.5, frame_mid_rect[3] // 2 - std_padding * 1.5),
    fill = COLORS["orange_dead"],
    layer = 1,
    function = lambda: ui_manager.menu_switch("facilities"),
    text = [
        Text(
            text = "FACILITIES",
            font = FONTS["topaz_m"],
            color = COLORS["orange_hi"],
            h_align = "center",
            v_align = "bottom",
            pad_x = s(2),
            pad_y = s(5),
        )
    ],
    image = [
        Image(
            png = "logo_facilities",
            scale = cover_scale,
            v_align = "top"
        )
    ]
)

ui_main_comms = UI(
    name = "main_comms",
    pos = (SQUARE_SIZE - ui_main_facilities.size[0] - std_padding, ui_main_facilities.pos[1]),
    size = ui_main_facilities.size,
    fill = COLORS["cyan_dead"],
    layer = 1,
    function = lambda: ui_manager.menu_switch("comms"),
    text = [
            Text(
                text = "COMMS",
                font = FONTS["topaz_m"],
                color = COLORS["cyan_hi"],
                h_align = "center",
                v_align = "bottom",
                pad_x = s(2),
                pad_y = s(5),
            )
        ],
    image = [
        Image(
            png = "logo_comms",
            scale = cover_scale,
            v_align = "top"
        )
    ]
)

#facilities menu UI elements-----------------------------------------------------------------

scroll_button_y = s(40)

ui_facilities_header = UI(
    name = "facilities_header",
    pos = (0, frame_hi_h + frame_border),
    size = (SQUARE_SIZE, std_padding * 2),
    fill = COLORS["transparent"],
    layer = 1,
    text = [
        Text(
            color = COLORS["orange_hi"],
            font = FONTS["topaz_xm"]
        )
    ]
)

ui_facilities_image = UI(
    name = "facilities_image",
    pos = (0, frame_hi_h + std_padding * 2 + frame_border),
    size = (image_size, image_size),
    fill = COLORS["orange_dead"],
    layer = 1,
    image = [
        Image(
            scale = img_scale
        )
    ]
)

ui_facilities_info = UI(
    name = "facilities_info",
    pos = (0, ui_facilities_image.pos[1] + ui_facilities_image.size[1]),
    size = (ui_facilities_image.size[0], s(340)),
    fill = COLORS["orange_dead"],
    layer = 1
)

ui_facilities_location = UI(
    name = "facilities_location",
    pos = (0, ui_facilities_info.pos[1]),
    size = (ui_facilities_info.size[0], s(42)),
    fill = COLORS["orange_lo"],
    layer = 2,
    text = [
        Text(
            text = "location",
            font = FONTS["topaz_s"],
            color = COLORS["orange_hi"],
            h_align = "left",
            v_align = "top",
            pad_x = s(5),
            pad_y = s(5)
        )
    ]
)

ui_facilities_staff = UI(
    name = "facilities_staff",
    pos = (0, ui_facilities_info.pos[1] + s(42) + frame_border),
    size = (ui_facilities_info.size[0], s(70)),
    fill = COLORS["blue_lo"],
    layer = 2,
    text = [
        Text(
            text = "staff",
            color = COLORS["cyan_mid"],
            h_align = "left",
            v_align = "bottom",
            pad_x = frame_border,
            pad_y = frame_border,
        ),
        Text(
            text = "?/max",
            font = FONTS["topaz_xm"],
            color = COLORS["cyan_hi"],
            h_align = "center",
            v_align = "top",
            pad_x = frame_border,
            pad_y = frame_border,
        )
    ]
)

ui_facilities_area = UI(
    name = "facilities_area",
    pos = (0, ui_facilities_staff.pos[1] + s(70) + frame_border),
    size = ui_facilities_staff.size,
    fill = COLORS["orange_lo"],
    layer = 2,
    text = [
        Text(
            text = "m²",
            color = COLORS["orange_mid"],
            h_align = "left",
            v_align = "bottom",
            pad_x = frame_border,
            pad_y = frame_border,
        ),
        Text(
            text = "?/max",
            font = FONTS["topaz_xm"],
            color = COLORS["orange_hi"],
            h_align = "center",
            v_align = "top",
            pad_x = frame_border,
            pad_y = frame_border,
        )
    ]
)

ui_facilities_power = UI(
    name = "facilities_power",
    pos = (0, ui_facilities_area.pos[1] + s(70) + frame_border),
    size = ui_facilities_area.size,
    fill = COLORS["orange_lo"],
    layer = 2,
    text = [
        Text(
            text = "/maxkW",
            color = COLORS["orange_mid"],
            h_align = "left",
            v_align = "bottom",
            pad_x = frame_border,
            pad_y = frame_border,
        ),
        Text(
            text = "?",
            font = FONTS["topaz_xm"],
            color = COLORS["orange_hi"],
            h_align = "center",
            v_align = "top",
            pad_x = frame_border,
            pad_y = frame_border,
        )
    ]
)

ui_facilities_manage = UI(
    name = "facilities_manage",
    pos = (0, ui_facilities_power.pos[1] + s(70) + frame_border),
    size = (ui_facilities_power.size[0], ui_facilities_power.size[1] - frame_border),
    fill = COLORS["black"],
    border = COLORS["yellow_border"],
    layer = 2,
    text = [
        Text(
            text = "manage",
            font = FONTS["topaz_xm"],
            color = COLORS["orange_hi"]
        )
    ]
)

icon_size = (s(147) - frame_border * 2) // 1.25
gc_pos_x = image_size + frame_border * 2
f_i_g_c_size = ((frame_mid_rect[2] - gc_pos_x) // 2 - frame_border, s(147))


for i in range(4):
    row = 0
    if i >= 2:
        row = 1
    globals()[f"ui_facilities_inventory_grid_cell_{i+1}"] = UI(
        name = f"facilities_inventory_grid_cell_{i+1}",
        pos = (gc_pos_x + i * (
                f_i_g_c_size[0] + frame_border * 2) - row * 2 * (
                f_i_g_c_size[0] + frame_border * 2),
               ui_facilities_image.pos[1] + row * (f_i_g_c_size[1] + frame_border * 2)),
        size = (f_i_g_c_size[0], s(147)),
        layer = 1,
        function = lambda: ui_manager.menu_switch("item"),
        text = [
            Text(
                text = "object",
                font = FONTS["topaz_m"],
                color = COLORS["orange_hi"],
                h_align = "left",
                v_align = "bottom",
                pad_x = frame_border,
                pad_y = frame_border
            ),
            Text(
                text = "in area",
                font = FONTS["topaz_s"],
                color = COLORS["orange_mid"],
                h_align = "right",
                v_align = "top",
                pad_x = frame_border,
                pad_y = frame_border,
            ),
            Text(
                text = "area",
                font = FONTS["topaz_m"],
                color = COLORS["orange_hi"],
                h_align = "right",
                v_align = "top",
                pad_x = frame_border,
                pad_y = frame_border + s(16)
            ),
            Text(
                text = "oid",
                color = COLORS["transparent"]
            )
        ]
    )
    grid_cell_pos = ui_manager.ui_lookup(f"facilities_inventory_grid_cell_{i+1}").pos

    globals()[f"ui_facilities_inventory_grid_cell_image_{i + 1}"] = UI(
        name = f"facilities_inventory_grid_cell_image_{i + 1}",
        pos = (grid_cell_pos[0] + frame_border, grid_cell_pos[1] + frame_border),
        size = (icon_size, icon_size),
        fill = COLORS["green_dead"],
        layer = 2,
        image = [
            Image(
                scale = icon_scale
            )
        ]
    )

f_scroll_x = (SQUARE_SIZE - image_size - frame_border * 2) // 2
f_scroll_pos_y = ui_facilities_image.pos[1] + f_i_g_c_size[1] * 2 + frame_border * 4

ui_facilities_inventory_up = UI(
    name = "facilities_inventory_up",
    pos = (gc_pos_x, f_scroll_pos_y),
    size = (f_scroll_x, scroll_button_y),
    fill = COLORS["gray_lo"],
    layer = 1,
    function = lambda: ui_manager.facilities_inventory_scroll(-1),
    text = [
        Text(
            text = "^",
            color = COLORS["black"],
            font = FONTS["topaz_xl"],
            v_align = "bottom",
            pad_y = s(7)
        )
    ]
)

ui_facilities_inventory_down = UI(
    name = "facilities_inventory_down",
    pos = (gc_pos_x + f_i_g_c_size[0] + frame_border, f_scroll_pos_y),
    size = ui_facilities_inventory_up.size,
    fill = COLORS["gray_lo"],
    layer = 1,
    function = lambda: ui_manager.facilities_inventory_scroll(1),
    text = [
        Text(
            text = "^",
            color = COLORS["black"],
            font = FONTS["topaz_xl"],
            v_align = "top",
            pad_y = s(-24),
            rotate = 180
        )
    ]
)

# item menu UI elements ----------------------------------------------------------------------------

ui_item_header = UI(
    name = "item_header",
    pos = ui_facilities_header.pos,
    size = (ui_facilities_header.size[0], ui_facilities_header.size[1] * 1.25),
    fill = COLORS["transparent"],
    layer = 0,
    text = [
        Text(
            text = "item",
            color = COLORS["green_hi"],
            font = FONTS["topaz_l"],
            v_align = "center",
            h_align = "left",
            pad_y = frame_border,
        )
    ]
)

ui_item_image = UI(
    name = "item_image",
    pos = (0, ui_item_header.pos[1] + ui_item_header.size[1] + frame_border),
    size = (image_size, image_size),
    fill = COLORS["green_dead"],
    layer = 0,
    image = [
        Image(
            scale = img_scale
        )
    ]
)

ui_item_description = UI(
    name = "item_description",
    pos = (ui_item_image.size[0] + frame_border, ui_item_header.pos[1] + ui_item_header.size[1] + frame_border),
    size = (ui_item_header.size[0] - ui_item_image.size[0] - frame_border,
            image_size // 1.5 + s(30)),
    fill = COLORS["green_dead"],
    layer = 0,
    text = [
        Text(
            text = "description",
            font = FONTS["topaz_m"],
            color = COLORS["white"],
            h_align = "left",
            v_align = "top",
            pad_x = frame_border * 2,
            pad_y = frame_border * 2
        )
    ]
)

i_c_g_c_size = (ui_item_description.size[0] // 2, s(147))
i_c_g_c_pos = (ui_item_description.pos[0],
               ui_item_description.pos[1] + ui_item_description.size[1] + frame_border)

for i in range(4):
    row = 0
    if i >= 2:
        row = 1
    globals()[f"ui_item_contents_grid_cell_{i+1}"] = UI(
        name = f"item_contents_grid_cell_{i+1}",
        pos = (i_c_g_c_pos[0] + i * (
                i_c_g_c_size[0] + frame_border) - row * 2 * (
                     i_c_g_c_size[0] + frame_border),
             i_c_g_c_pos[1] + frame_border + row * (i_c_g_c_size[1] + frame_border)),
        size = (ui_item_description.size[0] // 2 - frame_border, s(147)),
        layer = 1,
        function = lambda: ui_manager.item_display(),
        text = [
            Text(
                text = "object",
                font = FONTS["topaz_m"],
                color = COLORS["green_hi"],
                h_align = "left",
                v_align = "bottom",
                pad_x = frame_border,
                pad_y = frame_border
            ),
            Text(
                text = "weight",
                font = FONTS["topaz_s"],
                color = COLORS["green_mid"],
                h_align = "right",
                v_align = "top",
                pad_x = frame_border,
                pad_y = frame_border,
            ),
            Text(
                text = "volume",
                font = FONTS["topaz_m"],
                color = COLORS["green_hi"],
                h_align = "right",
                v_align = "top",
                pad_x = frame_border,
                pad_y = frame_border + s(16)
            ),
            Text(
                text = "oid",
                color = COLORS["transparent"]
            )
        ]
    )
    grid_cell_pos = ui_manager.ui_lookup(f"item_contents_grid_cell_{i+1}").pos

    globals()[f"ui_item_contents_grid_cell_image_{i + 1}"] = UI(
        name = f"item_contents_grid_cell_image_{i + 1}",
        pos = (grid_cell_pos[0] + frame_border, grid_cell_pos[1] + frame_border),
        size = (icon_size, icon_size),
        fill = COLORS["green_dead"],
        layer = 2,
        image = [
            Image(
                scale = icon_scale
            )
        ]
    )

i_scroll_y = (frame_lo_rect[1] - frame_border * 2 - scroll_button_y)
i_scroll_size_x = (ui_item_description.size[0] // 2)

ui_item_contents_up = UI(
    name = "item_contents_up",
    pos = (ui_item_description.pos[0], i_scroll_y),
    size = (i_scroll_size_x, scroll_button_y),
    fill = COLORS["green_dead"],
    layer = 0,
    function = lambda: ui_manager.item_contents_scroll(-1),
    text = [
        Text(
            text = "^",
            color = COLORS["black"],
            font = FONTS["topaz_xl"],
            v_align = "bottom",
            pad_y = s(7)
        )
    ]
)

ui_item_contents_down = UI(
    name = "item_contents_down",
    pos = (ui_item_description.pos[0] + i_scroll_size_x, i_scroll_y),
    size = (i_scroll_size_x, scroll_button_y),
    fill = COLORS["green_dead"],
    layer = 0,
    function = lambda: ui_manager.item_contents_scroll(1),
    text = [
        Text(
            text = "^",
            color = COLORS["black"],
            font = FONTS["topaz_xl"],
            v_align = "top",
            pad_y = s(-24),
            rotate = 180
        )
    ]
)

ui_item_info = UI(
    name = "item_info",
    pos = (ui_item_image.pos[0], ui_item_image.pos[1] + ui_item_image.size[1] + frame_border),
    size = (ui_item_image.size[0], frame_mid_rect[3] - ui_item_image.size[1]
            - ui_item_header.size[1] - frame_border * 4),
    fill = COLORS["green_dead"],
    layer = 0
)

ui_item_weight = UI(
    name = "item_weight",
    pos = ui_item_info.pos,
    size = (ui_item_info.size[0], s(60)),
    fill = COLORS["green_lo"],
    layer = 1,
    text = [
        Text(
            text = "weight",
            font = FONTS["topaz_s"],
            color = COLORS["green_mid"],
            h_align = "left",
            v_align = "top",
            pad_x = frame_border,
            pad_y = frame_border,
        ),
        Text(
            text = "kg",
            font = FONTS["topaz_m"],
            color = COLORS["green_hi"],
            h_align = "center",
            v_align = "bottom",
            pad_x = frame_border,
            pad_y = frame_border,
        )
    ]
)

ui_item_volume = UI(
    name = "item_volume",
    pos = (ui_item_weight.pos[0], ui_item_weight.pos[1] + ui_item_weight.size[1] + frame_border),
    size = ui_item_weight.size,
    fill = COLORS["green_lo"],
    layer = 1,
    text = [
        Text(
            text = "volume",
            font = FONTS["topaz_s"],
            color = COLORS["green_mid"],
            h_align = "left",
            v_align = "top",
            pad_x = frame_border,
            pad_y = frame_border
        ),
        Text(
            text = "L",
            font = FONTS["topaz_m"],
            color = COLORS["green_hi"],
            h_align = "center",
            v_align = "bottom",
            pad_x = frame_border,
            pad_y = frame_border
        )
    ]
)

# comms menu UI elements-----------------------------------------------------------------------------

comms_scroll_y_pos = (frame_mid_rect[1] + frame_mid_rect[3] - scroll_button_y - frame_border)

ui_comms_up = UI(
    name = "comms_up",
    pos = (frame_mid_rect[0], comms_scroll_y_pos),
    size = (frame_mid_rect[2] // 2, scroll_button_y),
    fill = COLORS["cyan_lo"],
    layer = 0,
    function = lambda: ui_manager.comms_scroll(-1),
    text = [
        Text(
            text = "^",
            color = COLORS["black"],
            font = FONTS["topaz_xl"],
            v_align = "bottom",
            pad_y = s(7)

        )
    ]
)

ui_comms_down = UI(
    name = "comms_down",
    pos = (frame_mid_rect[0] + ui_comms_up.size[0], comms_scroll_y_pos),
    size = ui_comms_up.size,
    fill = COLORS["cyan_lo"],
    layer = 0,
    function = lambda: ui_manager.comms_scroll(1),
    text = [
        Text(
            text = "^",
            font = FONTS["topaz_xl"],
            color = COLORS["black"],
            v_align = "top",
            pad_y = s(-24),
            rotate = 180
        )
    ]

)

comms_gc_size = (frame_mid_rect[3] - ui_comms_up.size[1] * 2 - std_padding * 2) // 3 - frame_border

comms_pfp_size = comms_gc_size

for i in range(3):
    globals()[f"ui_comms_grid_cell_{i + 1}"] = UI(
        name = f"comms_grid_cell_{i + 1}",
        pos = (frame_border + comms_gc_size, frame_hi_h + std_padding +
               i * (comms_gc_size + frame_border)),
        size = (frame_mid_rect[2] - comms_gc_size, comms_gc_size),
        fill = COLORS["cyan_lo"],
        layer = 0,
        function = lambda: ui_manager.menu_switch("convo"),
        text = [
            Text(
                text = "Firstname Lastname",
                font = FONTS["topaz_xm"],
                v_align = "top",
                h_align = "left",
                pad_x = frame_border * 2,
                pad_y = frame_border * 2
            ),
            Text(
                text = "title",
                font = FONTS["topaz_m"],
                color = COLORS["cyan_hi"],
                v_align = "top",
                h_align = "left",
                pad_y = std_padding * 2,
            ),
            Text(
                text = "Here will be the last message that was sent, should not be too long...",
                font = FONTS["topaz_s"],
                color = COLORS["cyan_mid"],
                v_align = "top",
                h_align = "left",
                pad_y = int(std_padding * 3.5),
                pad_x = frame_border * 2,
            ),
            Text(
                text = "cid",
                color = COLORS["transparent"]
            ),
            Text(
                text = "Day DD, HH:MM",
                font = FONTS["topaz_s"],
                color = COLORS["cyan_dead"],
                v_align = "bottom",
                h_align = "right",
                pad_y = frame_border
            )
        ]
    )

    grid_cell_pos = ui_manager.ui_lookup(f"comms_grid_cell_{i + 1}").pos

    globals()[f"ui_comms_grid_cell_image_{i + 1}"] = UI(
        name = f"comms_grid_cell_image_{i + 1}",
        pos = (grid_cell_pos[0] - comms_gc_size, grid_cell_pos[1]),
        size = (comms_pfp_size, comms_pfp_size),
        fill = COLORS["cyan_dead"],
        layer = 1,
        image = [
            Image(
                scale = pfp_scale
            )
        ]
        )

# convo menu UI elements -------------------------------------------------------------------------------------

convo_header_h = s(70)
convo_detail_w = s(70)

ui_convo_header = UI(
    name = "convo_header",
    pos = (0, frame_hi_h),
    size = (frame_hi_rect[2] - convo_detail_w, convo_header_h),
    fill = COLORS["blue_lo"],
    layer = 0,
    text = [
        Text(
            text = "Name Lastname",
            font = FONTS["topaz_l"],
            color = COLORS["cyan_hi"],
            h_align = "left",
            v_align = "bottom"
        )
    ]
)

ui_convo_detail = UI(
    name = "convo_detail",
    pos = (ui_convo_header.size[0], frame_hi_h),
    size = (convo_detail_w, convo_header_h),
    fill = COLORS["cyan_mid"],
    layer = 0,
    text = [
        Text(
            text = "=",
            font = FONTS["topaz_l"],
            color = COLORS["white"],
            v_align = "top",
            pad_y = frame_border + s(11),
        ),
        Text(
            text = "=",
            font = FONTS["topaz_l"],
            color = COLORS["white"],
            v_align = "bottom",
            pad_y = frame_border,
        )
    ]
)

convo_texting_h = s(180)
convo_scroll_y_pos = frame_mid_rect[1] + frame_mid_rect[3] - ui_comms_up.size[1] - frame_border - convo_texting_h
convo_send_size = (s(141), scroll_button_y)

ui_convo_down = UI(
    name = "convo_down",
    pos = (frame_mid_rect[0], convo_scroll_y_pos),
    size = (ui_comms_up.size[0] - convo_send_size[0] // 2, scroll_button_y),
    fill = COLORS["cyan_dead"],
    layer = 0,
    function = lambda: ui_manager.convo_scroll(1),
    text = [
        Text(
            text = "^",
            font = FONTS["topaz_xl"],
            color = COLORS["black"],
            v_align = "bottom",
            pad_y = s(7)

        )
    ]
)

ui_convo_send = UI(
    name = "convo_send",
    pos = (ui_convo_down.pos[0] + ui_convo_down.size[0], ui_convo_down.pos[1]),
    size = convo_send_size,
    fill = COLORS["blue_lo"],
    layer = 0,
    text = [
        Text(
            text = "send",
            font = FONTS["topaz_xm"],
            color = COLORS["black"],
            pad_x = frame_border,
            pad_y = frame_border,
        )
    ]
)

ui_convo_up = UI(
    name = "convo_up",
    pos = (frame_mid_rect[0] + ui_convo_down.size[0] + convo_send_size[0], convo_scroll_y_pos),
    size = ui_convo_down.size,
    fill = COLORS["cyan_dead"],
    layer = 0,
    function = lambda: ui_manager.convo_scroll(-1),
    text = [
        Text(
            text = "^",
            font = FONTS["topaz_xl"],
            color = COLORS["black"],
            v_align = "top",
            pad_y = s(-24),
            rotate = 180
        )
    ]

)

ui_convo_text_down = UI(
    name = "convo_text_down",
    pos = (frame_mid_rect[2] - scroll_button_y,
           frame_lo_rect[1] - convo_texting_h - frame_border),
    size = (scroll_button_y, convo_texting_h // 2),
    fill = COLORS["blue_dead"],
    layer = 0,
    text = [
        Text(
            text = "^",
            font = FONTS["topaz_xl"],
            color = COLORS["black"],
            h_align = "left",
            pad_x = s(-22),
            rotate = -90
        )
    ]
)

ui_convo_text_up = UI(
    name = "convo_text_up",
    pos = (ui_convo_text_down.pos[0], ui_convo_text_down.pos[1] + ui_convo_text_down.size[1]),
    size = ui_convo_text_down.size,
    fill = COLORS["blue_dead"],
    layer = 0,
    text = [
        Text(
            text = "^",
            font = FONTS["topaz_xl"],
            color = COLORS["black"],
            h_align = "right",
            pad_x = s(-16),
            rotate = 90
        )
    ]
)


pfp_icon_size = (ui_convo_up.pos[1] - frame_hi_h - ui_convo_header.size[1] - frame_border) // 4
c_g_c_size = (frame_mid_rect[2] - pfp_icon_size, pfp_icon_size)

for i in range(4):
    globals()[f"ui_convo_grid_cell_l_{i+1}"] = UI(
        name = f"convo_grid_cell_l_{i+1}",
        pos = (pfp_icon_size, frame_hi_h + ui_convo_header.size[1] + frame_border +
               i * c_g_c_size[1]),
        size = c_g_c_size,
        fill = COLORS["cyan_lo"],
        layer = 0,
        text = [
            Text(
                text = "Sample text of what a person might say over the course of one line, not too much?",
                font = FONTS["topaz_convo"],
                color = COLORS["cyan_hi"],
                h_align = "left",
                v_align = "top",
                pad_y = frame_border * 1,
                pad_x = frame_border * 3
            ),
            Text(
                text = format_time_short(12387.124),
                font = FONTS["topaz_s"],
                color = COLORS["gray_hi"],
                h_align = "right",
                v_align = "bottom",
                pad_y = 0,
                pad_x = 0,
            )
        ]
    )
    grid_cell_pos = ui_manager.ui_lookup(f"convo_grid_cell_l_{i+1}").pos
    globals()[f"ui_convo_grid_cell_l_pfp_{i+1}"] = UI(
        name = f"convo_grid_cell_l_pfp_{i+1}",
        pos = (grid_cell_pos[0] - pfp_icon_size, grid_cell_pos[1]),
        size = (pfp_icon_size, pfp_icon_size),
        fill = COLORS["cyan_dead"],
        layer = 0,
        image = [
            Image(
                png = "",
                scale = icon_scale // 2
            )
        ]
    )

    globals()[f"ui_convo_grid_cell_r_{i+1}"] = UI(
        name = f"convo_grid_cell_r_{i+1}",
        pos = (grid_cell_pos[0] - pfp_icon_size, grid_cell_pos[1]),
        size = c_g_c_size,
        fill = COLORS["orange_lo"],
        layer = 1,
        text = [
            Text(
                text = "Sample text of what a person might say over the course of one line, not too much?",
                font = FONTS["topaz_convo"],
                color = COLORS["orange_hi"],
                h_align = "left",
                v_align = "top",
                pad_y = frame_border * 1,
                pad_x = frame_border * 3
            ),
            Text(
                text = format_time_short(12387.124),
                font = FONTS["topaz_s"],
                color = COLORS["gray_hi"],
                h_align = "right",
                v_align = "bottom",
                pad_y = 0,
                pad_x = 0,
            )
        ]
    )
    globals()[f"ui_convo_grid_cell_r_pfp_{i+1}"] = UI(
        name = f"convo_grid_cell_r_pfp_{i+1}",
        pos = (frame_mid_rect[2] - pfp_icon_size, grid_cell_pos[1]),
        size = (pfp_icon_size, pfp_icon_size),
        fill = COLORS["orange_dead"],
        layer = 1 ,
        image = [
            Image(
                png = "",
                scale = icon_scale // 2
            )
        ]
    )

c_t_g_c_size = (frame_mid_rect[2] - scroll_button_y - frame_border * 2,
                (convo_texting_h - frame_border * 2) // 2)

for i in range(2):
    globals()[f"ui_convo_text_grid_cell_{i+1}"] = UI(
        name = f"convo_text_grid_cell_{i+1}",
        pos = (frame_border, ui_convo_text_down.pos[1] + frame_border +
               i * (c_t_g_c_size[1] + frame_border)),
        size = c_t_g_c_size,
        fill = COLORS["blue_lo"],
        layer = 0,
        text = [
            Text(
                text = "Sample text of what a person might say over the course of one line, not too much?",
                font = FONTS["topaz_convo"],
                color = COLORS["white"],
                h_align = "left",
                v_align = "top",
                pad_y = frame_border * 1,
                pad_x = frame_border * 3
            ),
        ]
    )