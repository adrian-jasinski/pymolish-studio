from pymol.Qt import QtGui


def readable(color, dark):
    """Named syntax colors were picked for a white page (blue, darkBlue,
    black); on a dark one keep the hue and raise the lightness."""
    c = QtGui.QColor(color)
    if dark and c.lightness() < 170:
        c = QtGui.QColor.fromHsl(c.hslHue(), c.hslSaturation(), 170)
    return c


def textformat(color, style=''):
    fmt = QtGui.QTextCharFormat()
    # ponytail: read once at import, so editors keep their colors when the
    # theme is toggled until restart; rebuild STYLES on toggle if that matters.
    dark = QtGui.QGuiApplication.palette().base().color().lightness() < 128
    fmt.setForeground(readable(color, dark))

    for word in style.split():
        if word == 'bold':
            fmt.setFontWeight(QtGui.QFont.Weight.Bold)
        elif word == 'italic':
            fmt.setFontItalic(True)
        elif word.startswith('bg:'):
            fmt.setBackground(QtGui.QColor(word[3:]))
        else:
            print('unhandled style:', word)

    return fmt
