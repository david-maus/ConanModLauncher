from PyQt5.QtGui import QPalette, QColor


WHITE       = QColor(255, 255, 255)
BLACK       = QColor(0  , 0  , 0)
RED         = QColor(255, 0  , 0)
PRIMARY     = QColor(53 , 53 , 53)
SECONDARY   = QColor(35 , 35 , 35)
TERTIARY    = QColor(42 , 130, 218)


def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())


class QDarkPalette(QPalette):
    """Set Dark palette for Qt meant to be used with the Fusion theme."""

    def __init__(self, *__args):
        """Initialize Palettes."""
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Start method to set the tooltip stylesheet to a `QtApplication`."""
        app.setStyleSheet("QToolTip {{"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)
