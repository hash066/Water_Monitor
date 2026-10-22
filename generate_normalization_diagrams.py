"""Generate normalization slides in the exact visual format of RVCE senior PDF.
Slide 1: Tables with FD brackets + Normalization Compliance Grid
Slide 2: Step-by-step Decomposition with branching arrows and split tables with FDs.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def create_slide_1(output_path):
    fig, ax = plt.subplots(figsize=(20, 11), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1100)
    ax.axis('off')

    # Top Banner
    banner = patches.FancyBboxPatch((700, 1020), 600, 52, boxstyle="round,pad=5,rounding_size=16",
                                    facecolor="#7CB342", edgecolor="#558B2F", linewidth=2)
    ax.add_patch(banner)
    ax.text(1000, 1046, "Normalization (1NF, 2NF, 3NF, BCNF)", 
            fontsize=20, fontweight='bold', color='white', ha='center', va='center')

    # Helper to draw an attribute box table
    def draw_table(title, attrs, x, y, box_w, box_h, bg_color, title_color="#263238"):
        ax.text(x, y + 26, title, fontsize=13, fontweight='bold', color=title_color, va='bottom')
        centers = []
        for i, attr in enumerate(attrs):
            bx = x + i * box_w
            rect = patches.FancyBboxPatch((bx, y), box_w - 4, box_h, boxstyle="round,pad=2,rounding_size=4",
                                          facecolor=bg_color, edgecolor="#455A64", linewidth=1.2)
            ax.add_patch(rect)
            weight = 'bold' if i == 0 else 'normal'
            ax.text(bx + (box_w - 4) / 2, y + box_h / 2, attr, fontsize=9.5, fontweight=weight,
                    color="#212121", ha='center', va='center')
            centers.append(bx + (box_w - 4) / 2)
        return centers

    # Helper to draw FD bracket line below table
    def draw_fd(source_x, target_xs, y_drop, label, line_color="#D32F2F", label_x_offset=-26):
        ax.plot([source_x, source_x], [y_drop + 15, y_drop], color=line_color, linewidth=1.5)
        min_x = min([source_x] + target_xs)
        max_x = max([source_x] + target_xs)
        ax.plot([min_x, max_x], [y_drop, y_drop], color=line_color, linewidth=1.5)
        for tx in target_xs:
            ax.annotate('', xy=(tx, y_drop + 15), xytext=(tx, y_drop),
                        arrowprops=dict(arrowstyle="->", color=line_color, lw=1.5))
        ax.text(source_x + label_x_offset, y_drop - 3, label, fontsize=10.5, fontweight='bold', color=line_color, ha='center', va='top')

    # Table 1: MONITORING_SITE
    c1 = draw_table("MONITORING_SITE", ["water_body_id", "name", "location_id", "region", "latitude", "longitude"],
                    x=50, y=880, box_w=170, box_h=35, bg_color="#FFCDD2") # Coral/Light Red
    draw_fd(c1[0], [c1[1], c1[2]], y_drop=845, label="FD1", line_color="#C2185B", label_x_offset=-26)
    draw_fd(c1[2], [c1[3], c1[4], c1[5]], y_drop=815, label="FD2", line_color="#7B1FA2", label_x_offset=-26)

    # Table 2: TELEMETRY_LOG
    c2 = draw_table("TELEMETRY_LOG", ["measurement_id", "sensor_id", "param_name", "measured_val", "recorded_at", "is_anomalous", "water_body_id", "installed_at"],
                    x=50, y=700, box_w=135, box_h=35, bg_color="#E1BEE7") # Lavender / Purple
    draw_fd(c2[0], [c2[1], c2[2], c2[3], c2[4], c2[5]], y_drop=665, label="FD1", line_color="#512DA8", label_x_offset=-26)
    draw_fd(c2[1], [c2[6], c2[7]], y_drop=635, label="FD2", line_color="#C2185B", label_x_offset=-26)

    # Table 3: INCIDENT_REGISTER
    c3 = draw_table("INCIDENT_REGISTER", ["pollution_event_id", "water_body_id", "location_id", "change_pct", "occurred_at", "state_id", "valid_from", "valid_to", "condition"],
                    x=50, y=520, box_w=125, box_h=35, bg_color="#BBDEFB") # Soft Blue
    draw_fd(c3[0], [c3[1], c3[2], c3[3], c3[4], c3[5]], y_drop=485, label="FD1", line_color="#1976D2", label_x_offset=-26)
    draw_fd(c3[5], [c3[6], c3[7], c3[8]], y_drop=455, label="FD2", line_color="#D32F2F", label_x_offset=-26)

    # Table 4: WEATHER_LOG
    c4 = draw_table("WEATHER_LOG", ["weather_id", "location_id", "rainfall_mm", "recorded_at"],
                    x=50, y=340, box_w=160, box_h=35, bg_color="#C8E6C9") # Soft Green
    draw_fd(c4[0], [c4[1], c4[2], c4[3]], y_drop=305, label="FD1", line_color="#388E3C", label_x_offset=-26)

    # Table 5: INSPECTION_RECORD
    c5 = draw_table("INSPECTION_RECORD", ["inspection_id", "water_body_id", "inspected_at", "findings"],
                    x=50, y=190, box_w=160, box_h=35, bg_color="#FFF9C4") # Soft Yellow
    draw_fd(c5[0], [c5[1], c5[2], c5[3]], y_drop=155, label="FD1", line_color="#F57C00", label_x_offset=-26)

    # Table 6: LAND_USE
    c6 = draw_table("LAND_USE", ["factor_id", "location_id", "name", "factor_type"],
                    x=50, y=60, box_w=160, box_h=35, bg_color="#FFE0B2") # Soft Orange
    draw_fd(c6[0], [c6[1], c6[2], c6[3]], y_drop=25, label="FD1", line_color="#E64A19", label_x_offset=-26)

    # ---------------- COMPLIANCE MATRIX (RIGHT SIDE) ----------------
    grid_x = 1240
    grid_y = 510
    cols = ["MON_SITE", "TELEM_LOG", "INC_REG", "WEATHER", "INSPEC", "LAND_USE"]
    rows = ["BCNF", "3NF", "2NF", "1NF"]
    data = [
        [False, False, False, True, True, True],
        [False, False, False, True, True, True],
        [True,  True,  True,  True, True, True],
        [True,  True,  True,  True, True, True]
    ]

    col_w = 115
    row_h = 75
    header_h = 55
    total_w = 130 + len(cols) * col_w
    total_h = header_h + len(rows) * row_h

    # Container panel
    panel = patches.FancyBboxPatch((grid_x, grid_y), total_w, total_h, boxstyle="round,pad=4,rounding_size=12",
                                   facecolor="#F8F9FA", edgecolor="#90A4AE", linewidth=1.5)
    ax.add_patch(panel)

    # Header row (Navy Blue)
    hdr_rect = patches.FancyBboxPatch((grid_x, grid_y + total_h - header_h), total_w, header_h,
                                      boxstyle="round,pad=2,rounding_size=8", facecolor="#1976D2", edgecolor="#1565C0")
    ax.add_patch(hdr_rect)

    # Header labels
    ax.text(grid_x + 65, grid_y + total_h - header_h / 2, "FORM", fontsize=11, fontweight='bold', color='white', ha='center', va='center')
    for j, c in enumerate(cols):
        cx = grid_x + 130 + j * col_w + col_w / 2
        ax.text(cx, grid_y + total_h - header_h / 2, c, fontsize=10, fontweight='bold', color='white', ha='center', va='center')

    # Grid rows
    for i, r_name in enumerate(rows):
        ry = grid_y + total_h - header_h - (i + 1) * row_h
        lbl_box = patches.Rectangle((grid_x, ry), 130, row_h, facecolor="#ECEFF1" if i % 2 == 0 else "#CFD8DC", edgecolor="#B0BEC5")
        ax.add_patch(lbl_box)
        ax.text(grid_x + 65, ry + row_h / 2, r_name, fontsize=13, fontweight='bold', color="#263238", ha='center', va='center')

        for j, val in enumerate(data[i]):
            cx = grid_x + 130 + j * col_w + col_w / 2
            cell_box = patches.Rectangle((grid_x + 130 + j * col_w, ry), col_w, row_h,
                                         facecolor="white" if i % 2 == 0 else "#FAFAFA", edgecolor="#ECEFF1")
            ax.add_patch(cell_box)
            if val:
                circle = patches.Circle((cx, ry + row_h / 2), radius=22, facecolor="#43A047", edgecolor="#2E7D32", lw=1.5)
                ax.add_patch(circle)
                ax.text(cx, ry + row_h / 2, "OK", fontsize=11, fontweight='bold', color='white', ha='center', va='center')
            else:
                circle = patches.Circle((cx, ry + row_h / 2), radius=22, facecolor="#E53935", edgecolor="#C62828", lw=1.5)
                ax.add_patch(circle)
                ax.text(cx, ry + row_h / 2, "FAIL", fontsize=9.5, fontweight='bold', color='white', ha='center', va='center')

    ax.text(grid_x + total_w / 2, grid_y - 20, "Failed 3NF/BCNF due to Transitive Dependencies (FD2)", 
            fontsize=12, fontweight='bold', color="#D32F2F", ha='center', va='top')
    ax.text(grid_x + total_w / 2, grid_y - 45, "Decomposed to BCNF in Slide 2", 
            fontsize=11, fontstyle='italic', color="#455A64", ha='center', va='top')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print("Slide 1 generated successfully:", output_path)


def create_slide_2(output_path):
    fig, ax = plt.subplots(figsize=(20, 11), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_xlim(0, 2000)
    ax.set_ylim(0, 1100)
    ax.axis('off')

    # Top Banner
    banner = patches.FancyBboxPatch((700, 1020), 600, 52, boxstyle="round,pad=5,rounding_size=16",
                                    facecolor="#7CB342", edgecolor="#558B2F", linewidth=2)
    ax.add_patch(banner)
    ax.text(1000, 1046, "Decomposition to BCNF (Eliminating Transitive FDs)", 
            fontsize=18, fontweight='bold', color='white', ha='center', va='center')

    def draw_table(title, attrs, x, y, box_w, box_h, bg_color):
        ax.text(x, y + 20, title, fontsize=12, fontweight='bold', color="#263238", va='bottom')
        centers = []
        for i, attr in enumerate(attrs):
            bx = x + i * box_w
            rect = patches.FancyBboxPatch((bx, y), box_w - 4, box_h, boxstyle="round,pad=2,rounding_size=4",
                                          facecolor=bg_color, edgecolor="#455A64", linewidth=1.2)
            ax.add_patch(rect)
            weight = 'bold' if i == 0 else 'normal'
            ax.text(bx + (box_w - 4) / 2, y + box_h / 2, attr, fontsize=9.5, fontweight=weight,
                    color="#212121", ha='center', va='center')
            centers.append(bx + (box_w - 4) / 2)
        return centers

    def draw_fd(source_x, target_xs, y_drop, label, line_color="#D32F2F", label_x_offset=-26):
        ax.plot([source_x, source_x], [y_drop + 15, y_drop], color=line_color, linewidth=1.5)
        min_x = min([source_x] + target_xs)
        max_x = max([source_x] + target_xs)
        ax.plot([min_x, max_x], [y_drop, y_drop], color=line_color, linewidth=1.5)
        for tx in target_xs:
            ax.annotate('', xy=(tx, y_drop + 15), xytext=(tx, y_drop),
                        arrowprops=dict(arrowstyle="->", color=line_color, lw=1.5))
        ax.text(source_x + label_x_offset, y_drop - 3, label, fontsize=10, fontweight='bold', color=line_color, ha='center', va='top')

    def draw_branch_arrows(parent_bottom_x, parent_bottom_y, left_top_x, left_top_y, right_top_x, right_top_y, arrow_color="#EC407A"):
        ax.annotate('', xy=(left_top_x, left_top_y), xytext=(parent_bottom_x - 60, parent_bottom_y),
                    arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, width=3, headwidth=10, headlength=10))
        ax.annotate('', xy=(right_top_x, right_top_y), xytext=(parent_bottom_x + 60, parent_bottom_y),
                    arrowprops=dict(facecolor=arrow_color, edgecolor=arrow_color, width=3, headwidth=10, headlength=10))

    # ================= CASE 1: MONITORING_SITE =================
    p1 = draw_table("MONITORING_SITE  (Violates 3NF/BCNF due to Transitive FD2)",
                    ["water_body_id", "name", "location_id", "region", "latitude", "longitude"],
                    x=540, y=900, box_w=145, box_h=32, bg_color="#FFCDD2")
    draw_fd(p1[0], [p1[1], p1[2]], y_drop=870, label="FD1", line_color="#C2185B", label_x_offset=-26)
    draw_fd(p1[2], [p1[3], p1[4], p1[5]], y_drop=845, label="FD2 (Transitive)", line_color="#7B1FA2", label_x_offset=-48)

    draw_branch_arrows(975, 820, 480, 765, 1480, 765, arrow_color="#EC407A")

    c1_1 = draw_table("WATER_BODY  [BCNF OK]",
                      ["water_body_id", "name", "location_id.."],
                      x=250, y=730, box_w=150, box_h=32, bg_color="#FFEBEE")
    draw_fd(c1_1[0], [c1_1[1], c1_1[2]], y_drop=700, label="FD1", line_color="#C2185B")

    c1_2 = draw_table("LOCATION  [BCNF OK]",
                      ["location_id", "region", "latitude", "longitude"],
                      x=1200, y=730, box_w=150, box_h=32, bg_color="#FFEBEE")
    draw_fd(c1_2[0], [c1_2[1], c1_2[2], c1_2[3]], y_drop=700, label="FD1", line_color="#7B1FA2")

    ax.plot([100, 1900], [650, 650], color="#CFD8DC", linestyle="--", linewidth=1.2)

    # ================= CASE 2: TELEMETRY_LOG =================
    p2 = draw_table("TELEMETRY_LOG  (Violates 3NF/BCNF due to Transitive FD2)",
                    ["measurement_id", "sensor_id", "param_name", "measured_val", "recorded_at", "is_anomalous", "water_body_id", "installed_at"],
                    x=450, y=560, box_w=135, box_h=32, bg_color="#E1BEE7")
    draw_fd(p2[0], [p2[1], p2[2], p2[3], p2[4], p2[5]], y_drop=530, label="FD1", line_color="#512DA8", label_x_offset=-26)
    draw_fd(p2[1], [p2[6], p2[7]], y_drop=505, label="FD2 (Transitive)", line_color="#C2185B", label_x_offset=-48)

    draw_branch_arrows(990, 480, 450, 425, 1490, 425, arrow_color="#AB47BC")

    c2_1 = draw_table("MEASUREMENT  [BCNF OK]",
                      ["measurement_id", "sensor_id..", "param_name", "measured_val", "recorded_at", "is_anomalous"],
                      x=120, y=390, box_w=125, box_h=32, bg_color="#F3E5F5")
    draw_fd(c2_1[0], [c2_1[1], c2_1[2], c2_1[3], c2_1[4], c2_1[5]], y_drop=360, label="FD1", line_color="#512DA8")

    c2_2 = draw_table("SENSOR  [BCNF OK]",
                      ["sensor_id", "water_body_id..", "installed_at"],
                      x=1260, y=390, box_w=150, box_h=32, bg_color="#F3E5F5")
    draw_fd(c2_2[0], [c2_2[1], c2_2[2]], y_drop=360, label="FD1", line_color="#C2185B")

    ax.plot([100, 1900], [310, 310], color="#CFD8DC", linestyle="--", linewidth=1.2)

    # ================= CASE 3: INCIDENT_REGISTER =================
    p3 = draw_table("INCIDENT_REGISTER  (Violates 3NF/BCNF due to Transitive FD2)",
                    ["pollution_event_id", "water_body_id", "location_id", "change_pct", "occurred_at", "state_id", "valid_from", "valid_to", "condition"],
                    x=410, y=220, box_w=130, box_h=32, bg_color="#BBDEFB")
    draw_fd(p3[0], [p3[1], p3[2], p3[3], p3[4], p3[5]], y_drop=190, label="FD1", line_color="#1976D2", label_x_offset=-26)
    draw_fd(p3[5], [p3[6], p3[7], p3[8]], y_drop=165, label="FD2 (Transitive)", line_color="#D32F2F", label_x_offset=-48)

    draw_branch_arrows(990, 140, 450, 85, 1490, 85, arrow_color="#42A5F5")

    c3_1 = draw_table("POLLUTION_EVENT  [BCNF OK]",
                      ["pollution_event_id", "water_body_id..", "location_id..", "state_id..", "change_pct", "occurred_at"],
                      x=120, y=50, box_w=125, box_h=32, bg_color="#E3F2FD")
    draw_fd(c3_1[0], [c3_1[1], c3_1[2], c3_1[3], c3_1[4], c3_1[5]], y_drop=20, label="FD1", line_color="#1976D2")

    c3_2 = draw_table("HISTORICAL_STATE  [BCNF OK]",
                      ["state_id", "water_body_id..", "valid_from", "valid_to", "condition"],
                      x=1190, y=50, box_w=135, box_h=32, bg_color="#E3F2FD")
    draw_fd(c3_2[0], [c3_2[1], c3_2[2], c3_2[3], c3_2[4]], y_drop=20, label="FD1", line_color="#D32F2F")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print("Slide 2 generated successfully:", output_path)

if __name__ == '__main__':
    create_slide_1("D:/Leave/WaterMonitor/normalization_slide1.png")
    create_slide_2("D:/Leave/WaterMonitor/normalization_slide2.png")
