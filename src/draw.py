from __future__ import annotations
from typing import Any, TYPE_CHECKING

import const
import drawsvg as dw

if TYPE_CHECKING:
  from tile import Tile, Property
  from board import Board

# Board dimensions: 1000x1000 total; player info in four quadrants at center
BOARD_SIZE = 1000
IMAGE_PADDING = 20  # Padding around the whole image
TILE_SIZE = BOARD_SIZE / 11  # 11 tiles along bottom and top
CENTER_MARGIN = 50  # Padding from inner board edge to player quadrants

# Font for all text (sans-serif; SVG often defaults to Times/serif)
FONT_FAMILY = "Helvetica"

# Property color name -> fill color for tiles
COLOR_MAP = {
    "brown": "#8B4513",
    "light_blue": "#87CEEB",
    "pink": "#FF69B4",
    "orange": "#FFA500",
    "red": "#DC143C",
    "yellow": "#FFD700",
    "green": "#228B22",
    "dark_blue": "#7070D0",
}


def tile_rect(position: int) -> tuple[float, float, float, float]:
    """Return (x, y, width, height) for the tile at given board position (0-39).
    Layout matches real Monopoly: GO bottom-right, play clockwise."""
    tw = TILE_SIZE
    if 0 <= position <= 10:
        # Bottom row: GO (0) at right, Jail (10) at left; leftward
        return (BOARD_SIZE - (position + 1) * tw, BOARD_SIZE - tw, tw, tw)
    if 11 <= position <= 20:
        # Left column: position 11 at bottom, 20 (Free Parking) at top; upward
        j = position - 11
        return (0, BOARD_SIZE - (j + 2) * tw, tw, tw)
    if 21 <= position <= 30:
        # Top row: position 21 at left, 30 (Go To Jail) at right; rightward
        k = position - 21
        return ((k + 1) * tw, 0, tw, tw)
    if 31 <= position <= 39:
        # Right column: position 31 at top, 39 at bottom; downward
        l = position - 31
        return (BOARD_SIZE - tw, (l + 1) * tw, tw, tw)
    return (0, 0, 0, 0)


def tile_center(position: int) -> tuple[float, float]:
    """Return (cx, cy) center of the tile at given position."""
    x, y, w, h = tile_rect(position)
    return (x + w / 2, y + h / 2)


def tile_fill_color(tile: Tile) -> str:
    """Return fill color for a tile based on its type/color."""
    if tile.tile_type() == "property":
        color = getattr(tile, "color", None)
        if color is not None:
            return COLOR_MAP.get(color, "#E0E0E0")
    if tile.tile_type() == "station":
        return "#E0E0E0"
    if tile.tile_type() == "utility":
        return "#E0E0E0"
    if tile.tile_type() == "special":
        if tile.name() == "GO":
            return "#90EE90"
        if "Jail" in tile.name() or "Visiting" in tile.name():
            return "#F5F5DC"
        if tile.name() == "Free Parking":
            return "#87CEEB"
        if tile.name() == "Go To Jail":
            return "#FFB6C1"
    if tile.tile_type() == "community_chest":
        return "#98FB98"
    if tile.tile_type() == "chance":
        return "#FFA500"
    if tile.tile_type() == "tax":
        return "#DDA0DD"
    return "#F5F5F5"


def draw_board_tiles(d: dw.Drawing, board: Board, show_number: bool = False) -> None:
    """Draw all tiles on the left board area."""
    for tile in board.tiles(): #type: ignore
        x, y, w, h = tile_rect(tile.position())
        fill = tile_fill_color(tile)
        d.append(dw.Rectangle(x, y, w, h, fill=fill, stroke="black", stroke_width=1))
        # Icon at top of tile for station, utility, chance, community_chest
        icon_y = y + 28
        cx = x + w / 2
        if tile.tile_type() == "station":
            d.append(
                dw.Text(
                    "🚆",
                    22,
                    cx,
                    icon_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        elif tile.tile_type() == "utility":
            icon = "💡" if "Electric" in tile.name() else "🚰"
            d.append(
                dw.Text(
                    icon,
                    22,
                    cx,
                    icon_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        elif tile.tile_type() == "chance":
            d.append(
                dw.Text(
                    "❓",
                    22,
                    cx,
                    icon_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        elif tile.tile_type() == "community_chest":
            d.append(
                dw.Text(
                    "💰",
                    22,
                    cx,
                    icon_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        elif tile.tile_type() == "tax":
            d.append(
                dw.Text(
                    "🏦",
                    22,
                    cx,
                    icon_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        elif tile.tile_type() == "special":
            if tile.name() == "GO":
                icon = "⭐"
            elif tile.name() == "Go To Jail":
                icon = "👮"
            elif "Jail" in tile.name() or "Visiting" in tile.name():
                icon = "⛓️"
            elif tile.name() == "Free Parking":
                icon = "🚗"
            else:
                icon = None
            if icon is not None:
                d.append(
                    dw.Text(
                        icon,
                        22,
                        cx,
                        icon_y,
                        text_anchor="middle",
                        dominant_baseline="middle",
                        font_family=FONT_FAMILY,
                    )
                )
        # Streets: horizontal line in the first fourth of the tile height (full width, lower)
        if tile.tile_type() == "property":
            line_y = y + h / 4
            d.append(
                dw.Line(
                    x,
                    line_y,
                    x + w,
                    line_y,
                    stroke="black",
                    stroke_width=1,
                )
            )
        # Tile name: one line per word, centered in the tile; buy price below for properties
        words = tile.name().split()
        if not words:
            words = [tile.name()]
        price = getattr(tile, "_price", None)
        if tile.tile_type() in ("property", "station", "utility") and price is not None:
            words.append(f"£{price}")
        cx, cy = x + w / 2, y + h / 2
        font_size = min(20, max(6, int(w / 8)))
        d.append(
            dw.Text(
                "\n".join(words),
                font_size,
                cx,
                cy,
                text_anchor="middle",
                dominant_baseline="middle",
                font_family=FONT_FAMILY,
            )
        )
        # Mortgaged properties: show "M" on the inside (inner corner)
        if tile.tile_type() in ("property", "station", "utility") and getattr(
            tile, "_is_mortgaged", False
        ):
            d.append(
                dw.Text(
                    "𝓜",
                    14,
                    x + w - 10,
                    y + 12,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_weight="bold",
                    fill="darkred",
                    font_family=FONT_FAMILY,
                )
            )
        # Owned properties: show owner number or piece in white at bottom right
        if tile.tile_type() in ("property", "station", "utility"):
            tile: Property
            owner = tile.owner
            if owner is not None:
                if show_number:
                    label = str(owner.index() + 1)
                else:
                    label = owner.piece()
                d.append(
                    dw.Text(
                        label,
                        12,
                        x + w - 8,
                        y + h - 6,
                        text_anchor="end",
                        dominant_baseline="alphabetic",
                        fill="white",
                        font_family=FONT_FAMILY,
                        # font_weight="bold",
                    )
                )


def draw_houses_and_hotels(d: dw.Drawing, board: Board) -> None:
    """Draw 🏠 for houses and 🏢 for hotels on street tiles."""
    for tile in board.tiles():
        if tile.tile_type() != "property":
            continue

        houses = getattr(tile, "_houses", 0)
        has_hotel = getattr(tile, "_has_hotel", 0)
        if houses == 0 and not has_hotel:
            continue

        x, y, w, _h = tile_rect(tile.position())
        # Row of house/hotel emojis at top of tile
        slot_w = min(w / 5, 14)
        gap = 4
        start_x = x + (w - (5 * slot_w + 4 * gap)) / 2
        base_y = y + 14
        emoji_size = 16
        for i in range(min(houses, 4)):
            cx = start_x + i * (slot_w + gap) + slot_w / 2
            d.append(
                dw.Text(
                    "🏠",
                    emoji_size,
                    cx,
                    base_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )
        if has_hotel:
            cx = start_x + 4 * (slot_w + gap) + slot_w / 2
            d.append(
                dw.Text(
                    "🏢",
                    emoji_size,
                    cx,
                    base_y,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )


def draw_player_circles(d: dw.Drawing, board: Board, show_number: bool = False) -> None:
    """Draw a circle for each player at their position (stacked if same tile)."""
    players = board.players()
    radius = 16
    # Distribute circles so they don't overlap on same tile
    for i, player in enumerate(players):
        if player.is_eliminated(): continue
        cx, cy = tile_center(player.position())
        same_tile = [
            j for j, p in enumerate(players) if p.position() == player.position()
        ]
        idx = same_tile.index(i)
        n_on_tile = len(same_tile)
        offset_x = (idx - (n_on_tile - 1) / 2) * (radius * 2.2)
        offset_y = (idx - (n_on_tile - 1) / 2) * (radius * 2.2) * 0.5
        px, py = cx + offset_x, cy + offset_y
        # Use player's lighter color for the circle fill (same as quadrant backgrounds)
        d.append(
            dw.Circle(
                px,
                py,
                radius,
                fill=player.color(),
                stroke="black",
                stroke_width=2,
            )
        )
        label = str(i + 1) if show_number else player.piece()
        d.append(
            dw.Text(
                label,
                10 if show_number else 18,
                px,
                py,
                text_anchor="middle",
                dominant_baseline="middle",
                font_family=FONT_FAMILY,
            )
        )


def _player_to_quadrant(player_index: int) -> int:
    """Map player index to quadrant index, swapping players 2 and 3.
    0->0 (top-left), 1->1 (top-right), 2->3 (bottom-right), 3->2 (bottom-left)."""
    if player_index == 2:
        return 3
    if player_index == 3:
        return 2
    return player_index


def _quadrant_rect(quadrant_index: int) -> tuple[float, float, float, float]:
    """Return (x, y, width, height) for player quadrant 0=top-left, 1=top-right, 2=bottom-left, 3=bottom-right."""
    tw = TILE_SIZE
    m = CENTER_MARGIN
    inner_left = tw + m
    inner_top = tw + m
    mid_x = BOARD_SIZE / 2
    mid_y = BOARD_SIZE / 2
    box_w = mid_x - inner_left - m / 2
    box_h = mid_y - inner_top - m / 2
    if quadrant_index == 0:  # top-left
        return (inner_left, inner_top, box_w, box_h)
    if quadrant_index == 1:  # top-right
        return (mid_x + m / 2, inner_top, box_w, box_h)
    if quadrant_index == 2:  # bottom-left
        return (inner_left, mid_y + m / 2, box_w, box_h)
    # bottom-right
    return (mid_x + m / 2, mid_y + m / 2, box_w, box_h)


# Unicode dice faces: ⚀ ⚁ ⚂ ⚃ ⚄ ⚅ (1–6)
DICE_EMOJI = "⚀⚁⚂⚃⚄⚅"


def draw_dice_in_current_player_box(d: dw.Drawing, board: Board) -> None:
    """Draw the two dice as emoji (⚀–⚅) in the bottom-right part of the current player's box."""
    die1, die2 = board.dice()
    current = board.current_player().index()
    if current >= 4:
        return
    quadrant = _player_to_quadrant(current)
    qx, qy, qw, qh = _quadrant_rect(quadrant)
    pad = 10
    size = 72
    gap = -8
    box_right = qx + qw
    box_bottom = qy + qh
    cy = box_bottom - pad - size / 2
    x1 = box_right - pad - size - gap - size / 2
    x2 = box_right - pad - size / 2
    for x, value in [(x1, die1), (x2, die2)]:
        if 1 <= value <= 6:
            d.append(
                dw.Text(
                    DICE_EMOJI[value - 1],
                    size,
                    x,
                    cy,
                    text_anchor="middle",
                    dominant_baseline="middle",
                    font_family=FONT_FAMILY,
                )
            )


# def draw_center_icon(d: dw.Drawing) -> None:
#    """Draw a big icon in the center of the board."""
#    cx, cy = BOARD_SIZE / 2, BOARD_SIZE / 2 + 8
#    d.append(
#        dw.Text(
#            "🤑",
#            60,
#            cx,
#            cy,
#            text_anchor="middle",
#            dominant_baseline="middle",
#            font_family=FONT_FAMILY,
#        )
#    )

def draw_players_center(d: dw.Drawing, board: Board, show_number: bool = False) -> None:
    """Draw player info in four quadrants around the center of the board."""
    players = board.players()
    if not players:
        return
    current = board.current_player()
    for i, player in enumerate(players):
        if i >= 4:
            break
        quadrant = _player_to_quadrant(i)
        qx, qy, qw, qh = _quadrant_rect(quadrant)
        # Use player's color for the quadrant background (lighter version for readability)
        fill = player.color()
        # Bolder border for current player
        stroke_width = 3 if i == current else 1
        d.append(
            dw.Rectangle(
                qx,
                qy,
                qw,
                qh,
                fill=fill,
                stroke="black",
                stroke_width=stroke_width,
            )
        )
        pad = 8
        line_h = 14
        ty = qy + pad + line_h
        header = (
            f"{i+1}. {player.name()}"
            if show_number
            else f"{player.piece()} {player.name()}"
        )
        d.append(
            dw.Text(
                header,
                20,
                qx + pad,
                ty,
                font_weight="bold",
                font_family=FONT_FAMILY,
            )
        )
        ty += line_h
        info_parts = [
            f"💵 £{player.balance()}",
            f"💳 {player.get_out_of_jail_free_cards}",
            f"⛓️ {player.turns_in_prison()}",
        ]
        info_text = " · ".join(info_parts)
        text_kw = {"fill": "red"} if player.is_in_prison() else {}
        d.append(
            dw.Text(info_text, 14, qx + pad, ty, font_family=FONT_FAMILY, **text_kw)
        )
        ty += line_h
        if player.owned_properties():
            ty += 2
            prop_font_size = 14
            prop_line_h = 17
            symbol_width = 20  # space reserved for symbol so names align
            d.append(
                dw.Text(
                    "Properties:",
                    prop_font_size,
                    qx + pad,
                    ty,
                    font_weight="bold",
                    font_family=FONT_FAMILY,
                )
            )
            ty += prop_line_h
            max_props = 8
            # Sort by position on the board
            sorted_props = sorted(player.owned_properties(), key=lambda p: p.position())
            for p in sorted_props[:max_props]:
                name_text = (
                    f"{p.name()} (M)" if getattr(p, "_is_mortgaged", False) else p.name()
                )
                # Symbol: ⬤ (color) for streets, 🚆 stations, 💡 electric, 🚰 water
                if p.tile_type() == "property":
                    # ⬤ with group color for streets (circle for reliable color)
                    color = getattr(p, "color", None)
                    fill = COLOR_MAP.get(color, "#808080") if color else "#808080"
                    d.append(
                        dw.Circle(
                            qx + pad + 6,
                            ty - 5,
                            5,
                            fill=fill,
                            stroke="black",
                            stroke_width=0.5,
                        )
                    )
                elif p.tile_type() == "station":
                    d.append(
                        dw.Text(
                            "🚆 ", prop_font_size, qx + pad, ty, font_family=FONT_FAMILY
                        )
                    )
                elif p.tile_type() == "utility":
                    symbol = "💡 " if "Electric" in p.name() else "🚰 "
                    d.append(
                        dw.Text(
                            symbol,
                            prop_font_size,
                            qx + pad,
                            ty,
                            font_family=FONT_FAMILY,
                        )
                    )
                # Property name (after symbol area)
                d.append(
                    dw.Text(
                        name_text,
                        prop_font_size,
                        qx + pad + symbol_width,
                        ty,
                        font_style=(
                            "italic" if getattr(p, "_is_mortgaged", False) else "normal"
                        ),
                        font_family=FONT_FAMILY,
                    )
                )
                ty += prop_line_h
            if len(player.owned_properties()) > max_props:
                d.append(
                    dw.Text(
                        f"+{len(player.owned_properties()) - max_props} more",
                        prop_font_size,
                        qx + pad,
                        ty,
                        fill="gray",
                        font_family=FONT_FAMILY,
                    )
                )


def draw(board: Board, svg_path: str = const.IMAGE_PATH, show_number: bool = False) -> None:
    """Draw the Monopoly game to board.svg: board with padding, players in four center quadrants."""
    total_size = BOARD_SIZE + 2 * IMAGE_PADDING
    d = dw.Drawing(total_size, total_size, id_prefix="board")
    # Group shifts content so the board has padding on all sides
    g: Any = dw.Group(transform=f"translate({IMAGE_PADDING}, {IMAGE_PADDING})")
    draw_board_tiles(g, board, show_number)
    draw_houses_and_hotels(g, board)
    draw_player_circles(g, board, show_number)
    # draw_center_icon(g)
    draw_players_center(g, board, show_number)
    draw_dice_in_current_player_box(g, board)
    d.append(g)
    d.save_svg(svg_path)