from pymol2 import SingletonPyMOL as PyMOL

import pymol

from pymol.Qt import QtCore
from pymol.Qt import QtGui
from pymol.Qt import QtWidgets
Gesture = QtCore.QEvent.Type.Gesture
Qt = QtCore.Qt

from .keymapping import get_modifiers
from .keymapping import get_wheel_button

# A pill on a see-through track; grey reads on a black and on a white
# viewport, whatever the theme of the window.
SEQ_SCROLL_STYLE = """
QScrollBar:horizontal { background: transparent; border: none; margin: 0; }
QScrollBar::handle:horizontal {
    background: rgba(128, 128, 128, 170); border-radius: 4px;
    min-width: 32px; margin: 3px 0; }
QScrollBar::handle:horizontal:hover, QScrollBar::handle:horizontal:pressed {
    background: rgba(160, 160, 160, 230); }
QScrollBar:horizontal:focus { border: 1px solid palette(highlight); }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent; }
"""

class PyMOLGLWidget(QtWidgets.QOpenGLWidget):
    '''
    PyMOL OpenGL Widget

    Can be used as a context manager to make OpenGL context current.
    '''

    # mouse button map
    _buttonMap = {
        Qt.MouseButton.LeftButton: 0,
        Qt.MouseButton.MiddleButton: 1,
        Qt.MouseButton.RightButton: 2,
    }

    def __enter__(self):
        '''
        Context manager to make the OpenGL context "current".

        Fixes depth-buffer issue with QOpenGLWidget
        https://github.com/schrodinger/pymol-open-source/issues/25
        '''
        self.makeCurrent()
        pymol._cmd._pushValidContext(self.cmd._COb)

    def __exit__(self, exc_type, exc_value, traceback):
        pymol._cmd._popValidContext(self.cmd._COb)

    def __init__(self, parent):
        self.gui = parent
        self.fb_scale = 1.0
        self._panel_edge = False  # pointer is on the internal GUI's left edge
        self._panel_drag = False  # ... and dragging it

        # OpenGL context setup
        f = QtGui.QSurfaceFormat()

        from pymol.invocation import options

        # logic equivalent to layer5/main.cpp:launch

        if options.multisample:
            f.setSamples(4)

        if options.force_stereo != -1:
            # See layer1/Setting.h for stereo modes

            if options.stereo_mode in (1, 12):
                f.setStereo(True)

        super().__init__(parent=parent)
        self.setFormat(f)
        self.setUpdateBehavior(self.UpdateBehavior.PartialUpdate)

        # pymol instance
        self.pymol = PyMOL()
        self.pymol.start()
        self.cmd = self.pymol.cmd

        # capture python output for feedback
        import pcatch
        pcatch._install()

        # for passive move drag
        self.setMouseTracking(True)

        # for accepting keyboard input (command line, shortcuts)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        # for idle rendering
        self._timer = QtCore.QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._pymolProcess)

        # drag n drop
        self.setAcceptDrops(True)

        # pinch-zoom
        self.grabGesture(Qt.GestureType.PinchGesture)

        # The scroll bar of the sequence viewer. The core draws the rows and
        # leaves a strip under them with marks for the selected residues;
        # this bar sits on the strip and is see-through, so the marks show.
        self.seq_scroll = bar = QtWidgets.QScrollBar(Qt.Orientation.Horizontal, self)
        bar.setObjectName("seq_scroll")
        bar.setAccessibleName("Scroll the sequence")
        bar.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        bar.setCursor(Qt.CursorShape.ArrowCursor)
        bar.setStyleSheet(SEQ_SCROLL_STYLE)
        bar.hide()
        bar.valueChanged.connect(self._seq_scrolled)

    def sizeHint(self):
        # default 640 + internal_gui, 480 + internal_feedback
        return QtCore.QSize(860, 498)

    ##########################
    # Input Events
    ##########################

    def event(self, ev):
        if ev.type() == Gesture:
            return self.gestureEvent(ev)

        return super().event(ev)

    def gestureEvent(self, ev):
        gesture = ev.gesture(Qt.GestureType.PinchGesture)

        if gesture is None:
            return False

        if gesture.state() == Qt.GestureState.GestureStarted:
            self.pinch_start_z = self.cmd.get_view()[11]

        changeFlags = gesture.changeFlags()

        if changeFlags & QtWidgets.QPinchGesture.ChangeFlag.RotationAngleChanged:
            delta = gesture.lastRotationAngle() - gesture.rotationAngle()
            self.cmd.turn('z', delta)

        if changeFlags & QtWidgets.QPinchGesture.ChangeFlag.ScaleFactorChanged:
            view = list(self.cmd.get_view())

            # best guess for https://bugreports.qt.io/browse/QTBUG-48138
            totalscalefactor = gesture.totalScaleFactor()
            if totalscalefactor == 1.0:
                totalscalefactor = gesture.scaleFactor()

            z = self.pinch_start_z / totalscalefactor
            delta = z - view[11]
            view[11] = z
            view[15] -= delta
            view[16] -= delta
            self.cmd.set_view(view)

        return True

    def _event_x_y_mod(self, ev):
        pos = ev.position() if hasattr(ev, "position") else ev.pos()
        return (
            int(self.fb_scale * pos.x()),
            int(self.fb_scale * (self.height() - pos.y())),
            get_modifiers(ev),
        )

    def _panel_width(self):
        """Width of the internal GUI in widget pixels, 0 when it is off."""
        get = self.cmd.get_setting_int
        if not get("internal_gui"):
            return 0
        return get("internal_gui_width") * get("display_scale_factor") / self.fb_scale

    def mouseMoveEvent(self, ev):
        x = ev.position().x()
        if self._panel_drag:
            dip = (self.width() - x) * self.fb_scale / self.cmd.get_setting_int(
                "display_scale_factor")
            self.cmd.set("internal_gui_width", max(100, int(dip)))
            return
        if not ev.buttons():
            # resize cursor on the left edge of the internal GUI
            width = self._panel_width()
            on_edge = bool(width) and abs(x - (self.width() - width)) < 4
            if on_edge != self._panel_edge:
                self._panel_edge = on_edge
                if on_edge:
                    self.setCursor(Qt.CursorShape.SplitHCursor)
                else:
                    self.unsetCursor()
        self.pymol.drag(*self._event_x_y_mod(ev))

    def mousePressEvent(self, ev, state=0):
        if ev.button() == Qt.MouseButton.LeftButton and (
                self._panel_drag or (state == 0 and self._panel_edge)):
            self._panel_drag = state == 0
            return
        if ev.button() not in self._buttonMap:
            return
        self.pymol.button(self._buttonMap[ev.button()], state,
                          *self._event_x_y_mod(ev))

    def mouseReleaseEvent(self, ev):
        self.mousePressEvent(ev, 1)

    def wheelEvent(self, ev):
        button = get_wheel_button(ev)
        if not button:
            return
        args = self._event_x_y_mod(ev)
        self.pymol.button(button, 0, *args)
        self.pymol.button(button, 1, *args)

    ##########################
    # OpenGL
    ##########################

    def paintGL(self):
        self.pymol.draw()
        self._place_seq_scroll()
        self._timer.start(0)

    def _seq_scrolled(self, value):
        pymol._cmd.seq_scroll(self.cmd._COb, value)
        self.update()

    def _place_seq_scroll(self):
        """After a frame: put the scroll bar on the strip the core left for
        it, with the range and position the core has now (the mouse wheel
        over the rows and a resize change them)."""
        bar = self.seq_scroll
        state = pymol._cmd.seq_scroll(self.cmd._COb, -1)
        if not state:
            bar.hide()
            return
        size, visible, first, left, bottom, right, top = (
            v if i < 3 else v / self.fb_scale for i, v in enumerate(state)
        )
        with QtCore.QSignalBlocker(bar):
            bar.setRange(0, size - visible)
            bar.setPageStep(visible)
            bar.setValue(first)
        bar.setGeometry(
            round(left),
            round(self.height() - top),
            round(right - left),
            round(top - bottom),
        )
        bar.show()

    def resizeGL(self, w, h):
        self.pymol.reshape(int(w * self.fb_scale), int(h * self.fb_scale), True)

    def updateFbScale(self, context):
        '''Update PyMOL's display scale factor from the window or screen context
        @type context: QWindow or QScreen
        '''
        self.fb_scale = context.devicePixelRatio()
        try:
            self.cmd.set('display_scale_factor', max(1, round(self.fb_scale)))
        except BaseException as e:
            # fails with modal draw (mpng ..., modal=1)
            print(e)

    def initializeGL(self):
        # Scale framebuffer for Retina displays
        try:
            window = self.windowHandle()

            # QOpenGLWidget workaround
            if window is None:
                window = self.parent().windowHandle()

            self.updateFbScale(window)
            window.screenChanged.connect(self.updateFbScale)
            window.screen().physicalDotsPerInchChanged.connect(
                    lambda dpi: self.updateFbScale(window))

        except AttributeError:
            pass

    def _pymolProcess(self):
        idle = self.pymol.idle()
        if idle or self.pymol.getRedisplay():
            self.update()

        self._timer.start(20)

    ##########################
    # drag n drop
    ##########################

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    url = url.toLocalFile()
                else:
                    url = url.toString()
                self.gui.load_dialog(url)
            event.accept()
