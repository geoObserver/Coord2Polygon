# -----------------------------------------------------------------------------#
# Title:       coord2polygon - QGIS-Plugin                                     #
# Author:      Mike Elstermann (#geoObserver)                                  #
# Version:     v0.5                                                            #
# Created:     04.08.2026                                                      #
# Last Change: 11.08.2026                                                      #
# see also:    https://geoobserver.de/qgis-plugins/                            #
#                                                                              #
# This file contains code generated with assistance from an AI                 #
# No warranty is provided for AI-generated portions.                           #
# Human review and modification performed by: Mike Elstermann (#geoObserver)   #
# -----------------------------------------------------------------------------#

import os

from qgis.PyQt.QtGui import QIcon

try:
    # Qt5
    from qgis.PyQt.QtWidgets import QAction
except ImportError:
    # Qt6
    from qgis.PyQt.QtGui import QAction

from qgis.PyQt.QtCore import Qt

from qgis.PyQt.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QDialogButtonBox,
    QCheckBox,
    QLabel,
    QGroupBox,
    QToolBar,
)

from qgis.core import (
    QgsMapLayer,
    QgsWkbTypes,
    QgsPointXY,
    QgsGeometry,
    QgsFeature,
    QgsFillSymbol,
    QgsSingleSymbolRenderer,
    QgsMarkerSymbol,
    QgsMarkerLineSymbolLayer,
    QgsUnitTypes,
    QgsProject,
    QgsVectorLayer,
)


# -----------------------------------------------------------------
# Qt5 / Qt6 compatibility
# -----------------------------------------------------------------

try:
    # Qt5
    TOOL_BUTTON_ICON_ONLY = Qt.ToolButtonIconOnly
except AttributeError:
    # Qt6
    TOOL_BUTTON_ICON_ONLY = Qt.ToolButtonStyle.ToolButtonIconOnly


try:
    # Qt6 / PyQt6
    DIALOG_BUTTON_OK = QDialogButtonBox.StandardButton.Ok
    DIALOG_BUTTON_CANCEL = QDialogButtonBox.StandardButton.Cancel
except AttributeError:
    # Qt5 / PyQt5
    DIALOG_BUTTON_OK = QDialogButtonBox.Ok
    DIALOG_BUTTON_CANCEL = QDialogButtonBox.Cancel


try:
    # Qt6 / PyQt6
    DIALOG_ACCEPTED = QDialog.DialogCode.Accepted
except AttributeError:
    # Qt5 / PyQt5
    DIALOG_ACCEPTED = QDialog.Accepted


try:
    # Qt6 / PyQt6
    MESSAGE_YES = QMessageBox.StandardButton.Yes
    MESSAGE_NO = QMessageBox.StandardButton.No
except AttributeError:
    # Qt5 / PyQt5
    MESSAGE_YES = QMessageBox.Yes
    MESSAGE_NO = QMessageBox.No


def exec_dialog(dialog):
    """
    Execute a dialog with either Qt5 or Qt6 syntax.
    """

    exec_method = getattr(dialog, "exec", None)

    if exec_method is not None:
        return exec_method()

    return dialog.exec_()


# -----------------------------------------------------------------
# Input dialog
# -----------------------------------------------------------------


class Coord2PolygonDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Coord2Polygon - Create polygon from coordinates")

        self.setMinimumWidth(600)

        main_layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Input type
        # ---------------------------------------------------------
        input_type_group = QGroupBox("Input type")

        input_type_layout = QVBoxLayout(input_type_group)

        self.rectangle_radio = QRadioButton(
            "Rectangle using xmin, ymin, xmax, ymax"
        )

        self.polyline_radio = QRadioButton(
            "Polyline using multiple coordinate pairs"
        )

        self.rectangle_radio.setChecked(True)

        self.input_type_button_group = QButtonGroup(self)

        self.input_type_button_group.addButton(self.rectangle_radio)

        self.input_type_button_group.addButton(self.polyline_radio)

        input_type_layout.addWidget(self.rectangle_radio)

        input_type_layout.addWidget(self.polyline_radio)

        main_layout.addWidget(input_type_group)

        # ---------------------------------------------------------
        # Rectangle coordinates
        # ---------------------------------------------------------
        self.rectangle_group = QGroupBox("Rectangle coordinates")

        rectangle_layout = QFormLayout(self.rectangle_group)

        self.xmin_edit = QLineEdit()
        self.ymin_edit = QLineEdit()
        self.xmax_edit = QLineEdit()
        self.ymax_edit = QLineEdit()

        self.xmin_edit.setPlaceholderText("e.g. 450000 or 450000,25")

        self.ymin_edit.setPlaceholderText("e.g. 5700000 or 5700000,75")

        self.xmax_edit.setPlaceholderText("e.g. 451000 or 451000.25")

        self.ymax_edit.setPlaceholderText("e.g. 5700500 or 5700500.50")

        rectangle_layout.addRow("xmin:", self.xmin_edit)

        rectangle_layout.addRow("ymin:", self.ymin_edit)

        rectangle_layout.addRow("xmax:", self.xmax_edit)

        rectangle_layout.addRow("ymax:", self.ymax_edit)

        main_layout.addWidget(self.rectangle_group)

        # ---------------------------------------------------------
        # Polyline coordinates
        # ---------------------------------------------------------
        self.polyline_group = QGroupBox("Polyline coordinates")

        polyline_layout = QVBoxLayout(self.polyline_group)

        help_text = QLabel(
            "Enter one coordinate pair per line using the format x;y.\n"
            "The semicolon separates the X and Y values.\n"
            "Both comma and period are accepted as decimal separators.\n"
            "The polygon is closed automatically if necessary.\n\n"
            "Example:\n"
            "450000;5700000\n"
            "451000;5700000\n"
            "451000;5700500\n"
            "450000;5700500"
        )

        help_text.setStyleSheet("color: gray;")

        self.coordinates_text = QTextEdit()

        self.coordinates_text.setPlaceholderText(
            "450000;5700000\n"
            "451000;5700000\n"
            "451000,5;5700500.25\n"
            "450000.25;5700500,75"
        )

        self.coordinates_text.setMinimumHeight(220)

        polyline_layout.addWidget(help_text)

        polyline_layout.addWidget(self.coordinates_text)

        main_layout.addWidget(self.polyline_group)

        # ---------------------------------------------------------
        # Save option
        # ---------------------------------------------------------
        self.save_changes_checkbox = QCheckBox(
            "Automatically save changes after creating the polygon"
        )

        main_layout.addWidget(self.save_changes_checkbox)

        # ---------------------------------------------------------
        # Dialog buttons
        # ---------------------------------------------------------
        self.button_box = QDialogButtonBox(
            DIALOG_BUTTON_OK | DIALOG_BUTTON_CANCEL
        )

        self.button_box.button(DIALOG_BUTTON_OK).setText("Create polygon")

        self.button_box.button(DIALOG_BUTTON_CANCEL).setText("Cancel")

        self.button_box.accepted.connect(self.accept)

        self.button_box.rejected.connect(self.reject)

        main_layout.addWidget(self.button_box)

        # ---------------------------------------------------------
        # Input type switching
        # ---------------------------------------------------------
        self.rectangle_radio.toggled.connect(self.update_input_type)

        self.update_input_type()

    def update_input_type(self):
        rectangle_enabled = self.rectangle_radio.isChecked()

        self.rectangle_group.setEnabled(rectangle_enabled)

        self.polyline_group.setEnabled(not rectangle_enabled)

    @staticmethod
    def text_to_float(text, field_name):
        """
        Accept both decimal points and decimal commas.
        """

        text = text.strip()

        if not text:
            raise ValueError(
                "The field '{}' must not be empty.".format(field_name)
            )

        text = text.replace(",", ".")

        try:
            return float(text)

        except ValueError:
            raise ValueError(
                "The field '{}' does not contain a valid number.".format(
                    field_name
                )
            )

    def get_rectangle_points(self):
        xmin = self.text_to_float(self.xmin_edit.text(), "xmin")

        ymin = self.text_to_float(self.ymin_edit.text(), "ymin")

        xmax = self.text_to_float(self.xmax_edit.text(), "xmax")

        ymax = self.text_to_float(self.ymax_edit.text(), "ymax")

        if xmin >= xmax:
            raise ValueError("xmin must be smaller than xmax.")

        if ymin >= ymax:
            raise ValueError("ymin must be smaller than ymax.")

        return [
            QgsPointXY(xmin, ymin),
            QgsPointXY(xmax, ymin),
            QgsPointXY(xmax, ymax),
            QgsPointXY(xmin, ymax),
            QgsPointXY(xmin, ymin),
        ]

    def get_polyline_points(self):
        text = self.coordinates_text.toPlainText().strip()

        if not text:
            raise ValueError("Please enter at least three coordinate pairs.")

        points = []

        for line_number, line in enumerate(text.splitlines(), start=1):
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            values = line.split(";")

            if len(values) != 2:
                raise ValueError(
                    "Line {} must contain exactly two values "
                    "in the format x;y.\n\n"
                    "Invalid line:\n{}".format(line_number, line)
                )

            x_text = values[0].strip()
            y_text = values[1].strip()

            if not x_text or not y_text:
                raise ValueError(
                    "Line {} contains an empty coordinate.".format(line_number)
                )

            try:
                x = float(x_text.replace(",", "."))

                y = float(y_text.replace(",", "."))

            except ValueError:
                raise ValueError(
                    "Invalid coordinate in line {}:\n{}\n\n"
                    "Valid examples:\n"
                    "450000;5700000\n"
                    "450000,25;5700000.5".format(line_number, line)
                )

            points.append(QgsPointXY(x, y))

        if len(points) < 3:
            raise ValueError(
                "A polygon requires at least three coordinate pairs."
            )

        first_point = points[0]
        last_point = points[-1]

        if first_point != last_point:
            points.append(QgsPointXY(first_point.x(), first_point.y()))

        return points

    def get_polygon_points(self):
        if self.rectangle_radio.isChecked():
            return self.get_rectangle_points()

        return self.get_polyline_points()


# -----------------------------------------------------------------
# Apply layer style
# -----------------------------------------------------------------


def apply_coord2polygon_style(layer):
    """
    Apply the Coord2Polygon fill, outline,
    and vertex marker style.
    """

    # Polygon fill and 0.5 mm outline
    symbol = QgsFillSymbol.createSimple(
        {
            "color": "255,128,128,255",
            "outline_color": "255,0,0,255",
            "outline_width": "0.5",
            "outline_width_unit": "MM",
            "outline_style": "solid",
        }
    )

    # Circle marker at every polygon vertex
    marker_symbol = QgsMarkerSymbol.createSimple(
        {
            "name": "circle",
            "color": "255,64,64,255",
            "outline_color": "255,0,0,255",
            "outline_width": "1",
            "size": "6",
            "size_unit": "Pixel",
            "outline_width_unit": "Pixel",
        }
    )

    try:
        # Older QGIS versions
        marker_symbol.setOutputUnit(QgsUnitTypes.RenderPixels)

    except AttributeError:
        # Newer QGIS versions
        marker_symbol.setOutputUnit(QgsUnitTypes.RenderUnit.RenderPixels)

    marker_line = QgsMarkerLineSymbolLayer()

    marker_line.setSubSymbol(marker_symbol)

    try:
        # Older QGIS versions
        marker_line.setPlacement(QgsMarkerLineSymbolLayer.Vertex)

    except AttributeError:
        # Newer QGIS versions
        marker_line.setPlacement(QgsMarkerLineSymbolLayer.Placement.Vertex)

    marker_line.setRotateMarker(False)

    symbol.appendSymbolLayer(marker_line)

    # 66 percent transparency equals 34 percent opacity
    symbol.setOpacity(0.34)

    layer.setRenderer(QgsSingleSymbolRenderer(symbol))

    layer.triggerRepaint()


# -----------------------------------------------------------------
# Get or create temporary result layer
# -----------------------------------------------------------------


def get_or_create_result_layer(iface):
    """
    Find or create the temporary polygon memory layer
    named Coord2Polygon.
    """

    project = QgsProject.instance()

    # Reuse an existing polygon vector layer
    # with the exact name.
    for candidate in project.mapLayers().values():

        if candidate.name() != "Coord2Polygon":
            continue

        if not isinstance(candidate, QgsVectorLayer):
            raise ValueError(
                "A layer named 'Coord2Polygon' exists, "
                "but it is not a vector layer."
            )

        if candidate.geometryType() != (QgsWkbTypes.PolygonGeometry):
            raise ValueError(
                "A layer named 'Coord2Polygon' exists, "
                "but it is not a polygon layer."
            )

        return candidate

    # Use the active layer CRS where available.
    # Otherwise use the project CRS.
    active_layer = iface.activeLayer()

    if active_layer is not None and active_layer.crs().isValid():
        crs = active_layer.crs()
    else:
        crs = project.crs()

    # Create a temporary polygon memory layer.
    result_layer = QgsVectorLayer("Polygon", "Coord2Polygon", "memory")

    if not result_layer.isValid():
        raise ValueError(
            "The temporary Coord2Polygon vector layer " "could not be created."
        )

    if crs.isValid():
        result_layer.setCrs(crs)

    result_layer.setCustomProperty("coord2polygon/temporary", True)

    project.addMapLayer(result_layer)

    return result_layer


# -----------------------------------------------------------------
# QGIS plugin class
# -----------------------------------------------------------------


class Coord2PolygonPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.toolbar = None
        self.toolbar_created_by_plugin = False

    def initGui(self):
        main_window = self.iface.mainWindow()

        icon_path = os.path.join(
            os.path.dirname(__file__),
            #            "icon.svg"
            #            "logo.png"
            "logo.svg",
        )

        # Create an icon-only QAction.
        self.action = QAction(QIcon(icon_path), "Coord2Polygon", main_window)

        self.action.setToolTip("Create polygon from coordinates")

        self.action.setStatusTip("Create polygon from coordinates")

        self.action.setIconVisibleInMenu(True)

        self.action.triggered.connect(self.run)

        # Find an existing geoObserverTools toolbar
        # by object name or title.
        self.toolbar = main_window.findChild(QToolBar, "geoObserverTools")

        if self.toolbar is None:

            for candidate in main_window.findChildren(QToolBar):

                if candidate.windowTitle() == ("geoObserverTools"):
                    self.toolbar = candidate
                    break

        # Create the toolbar if it does not exist.
        if self.toolbar is None:

            self.toolbar = main_window.addToolBar("geoObserverTools")

            self.toolbar.setObjectName("geoObserverTools")

            self.toolbar_created_by_plugin = True

        self.toolbar.setToolButtonStyle(TOOL_BUTTON_ICON_ONLY)

        self.toolbar.addAction(self.action)

        self.iface.addPluginToMenu("&Coord2Polygon", self.action)

    def unload(self):

        if self.action is not None:

            self.iface.removePluginMenu("&Coord2Polygon", self.action)

            if self.toolbar is not None:
                self.toolbar.removeAction(self.action)

            self.action.deleteLater()
            self.action = None

        # Remove only a toolbar created by this plugin.
        if self.toolbar_created_by_plugin and self.toolbar is not None:

            self.iface.mainWindow().removeToolBar(self.toolbar)

            self.toolbar.deleteLater()
            self.toolbar = None

    def run(self):

        # The active layer is not used as the destination.
        # It is used only for the CRS of a new result layer.
        dialog = Coord2PolygonDialog(self.iface.mainWindow())

        if exec_dialog(dialog) != DIALOG_ACCEPTED:
            return

        try:
            points = dialog.get_polygon_points()

        except ValueError as error:
            QMessageBox.critical(
                self.iface.mainWindow(), "Invalid input", str(error)
            )
            return

        geometry = QgsGeometry.fromPolygonXY([points])

        if geometry.isEmpty():
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                "The polygon geometry could not be created.",
            )
            return

        if not geometry.isGeosValid():

            answer = QMessageBox.warning(
                self.iface.mainWindow(),
                "Possibly invalid geometry",
                "The generated geometry may be invalid.\n\n"
                "Possible causes include:\n"
                "- self-intersecting lines\n"
                "- duplicate or problematic points\n"
                "- an invalid polygon shape\n\n"
                "Do you want to add the polygon anyway?",
                MESSAGE_YES | MESSAGE_NO,
                MESSAGE_NO,
            )

            if answer != MESSAGE_YES:
                return

        try:
            layer = get_or_create_result_layer(self.iface)

        except ValueError as error:
            QMessageBox.critical(
                self.iface.mainWindow(), "Result layer error", str(error)
            )
            return

        was_editable = layer.isEditable()

        if not was_editable and not layer.startEditing():
            QMessageBox.critical(
                self.iface.mainWindow(),
                "Editing error",
                "The temporary Coord2Polygon layer "
                "could not be switched to editing mode.",
            )
            return

        feature = QgsFeature(layer.fields())

        feature.setGeometry(geometry)

        if not layer.addFeature(feature):

            if not was_editable:
                layer.rollBack()

            QMessageBox.critical(
                self.iface.mainWindow(),
                "Error",
                "The polygon could not be added to "
                "the temporary Coord2Polygon layer.",
            )
            return

        # Commit immediately.
        # The memory layer remains temporary.
        if not layer.commitChanges():

            QMessageBox.critical(
                self.iface.mainWindow(),
                "Save error",
                "The polygon could not be committed "
                "to the temporary layer.",
            )

            return

        layer.updateExtents()

        apply_coord2polygon_style(layer)

        self.iface.setActiveLayer(layer)

        self.iface.mapCanvas().refresh()

        QMessageBox.information(
            self.iface.mainWindow(),
            "Success",
            "The polygon was created in the temporary " "Coord2Polygon layer.",
        )
