from __future__ import annotations

from PySide6.QtCore import QEasingCurve, Qt, QTimer, Signal, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QFontMetrics, QLinearGradient, QPainter, QPainterPath, QPen, QWheelEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from stratbox_windows.presentation.common.scenario_chat.models import ScenarioChatMessage
from stratbox_windows.presentation.qt_desktop.components.status_chip import StatusChip
from stratbox_windows.presentation.qt_desktop.theme.strategy_palette import resolve_avatar_gradient


class AvatarBadge(QWidget):
    def __init__(self, text: str, *, actor_kind: str, palette_key: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('scenarioAvatarBadge')
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setFixedSize(36, 36)
        self._text = text
        self._actor_kind = actor_kind
        self._palette_key = palette_key

    def set_avatar(self, text: str, *, actor_kind: str, palette_key: str) -> None:
        self._text = text
        self._actor_kind = actor_kind
        self._palette_key = palette_key
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        gradient_def = resolve_avatar_gradient(actor_kind=self._actor_kind, palette_key=self._palette_key)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor(gradient_def.start))
        gradient.setColorAt(1.0, QColor(gradient_def.end))

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addEllipse(rect)
        painter.fillPath(path, gradient)
        painter.setPen(QPen(QColor(gradient_def.border), 1))
        painter.drawEllipse(rect)

        font = QFont(self.font())
        font.setBold(True)
        font.setPointSize(max(9, font.pointSize() + 1))
        painter.setFont(font)
        painter.setPen(QColor(gradient_def.text))
        painter.drawText(self.rect(), Qt.AlignCenter, self._text[:2])


class ScenarioCaseBubble(QFrame):
    clicked = Signal(str)
    artifact_open_requested = Signal(str)

    def __init__(self, message: ScenarioChatMessage, parent=None) -> None:
        super().__init__(parent)
        self._message = message
        self._case_id = message.source_case_id
        self.setObjectName('scenarioCaseBubble')
        self.setProperty('tone', message.tone)
        self.setProperty('placement', message.placement)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 16, 18, 16)
        self._layout.setSpacing(10)

        meta = QHBoxLayout()
        meta.setContentsMargins(0, 0, 0, 0)
        meta.setSpacing(8)
        self._author = QLabel(self)
        self._author.setObjectName('chatMeta')
        meta.addWidget(self._author)
        meta.addStretch(1)
        self._status_chip = StatusChip(parent=self)
        meta.addWidget(self._status_chip)
        self._layout.addLayout(meta)

        self._title = QLabel(self)
        self._title.setObjectName('chatMessageTitle')
        self._title.setWordWrap(True)
        self._layout.addWidget(self._title)

        self._summary = QLabel(self)
        self._summary.setObjectName('chatMessageBody')
        self._summary.setWordWrap(True)
        self._layout.addWidget(self._summary)

        self._stage = QLabel(self)
        self._stage.setObjectName('chatStage')
        self._stage.setWordWrap(True)
        self._layout.addWidget(self._stage)

        self._params = QLabel(self)
        self._params.setObjectName('chatMeta')
        self._params.setWordWrap(True)
        self._layout.addWidget(self._params)

        self._steps_title = QLabel('Шаги', self)
        self._steps_title.setObjectName('composerSectionTitle')
        self._layout.addWidget(self._steps_title)
        self._steps_host = QWidget(self)
        self._steps_layout = QVBoxLayout(self._steps_host)
        self._steps_layout.setContentsMargins(0, 0, 0, 0)
        self._steps_layout.setSpacing(6)
        self._layout.addWidget(self._steps_host)

        self._artifacts_title = QLabel('Артефакты', self)
        self._artifacts_title.setObjectName('composerSectionTitle')
        self._layout.addWidget(self._artifacts_title)
        self._artifacts_host = QWidget(self)
        self._artifacts_layout = QVBoxLayout(self._artifacts_host)
        self._artifacts_layout.setContentsMargins(0, 0, 0, 0)
        self._artifacts_layout.setSpacing(6)
        self._layout.addWidget(self._artifacts_host)

        self.set_message(message)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if self._case_id:
            self.clicked.emit(self._case_id)
        super().mousePressEvent(event)

    def suggested_width(self) -> int:
        body_font = self._summary.font()
        title_font = self._title.font()
        metrics = QFontMetrics(body_font)
        title_metrics = QFontMetrics(title_font)
        samples = [
            title_metrics.horizontalAdvance(self._message.title[:80]) + 8,
            metrics.horizontalAdvance(self._message.summary[:120]) + 8,
        ]
        if self._message.stage_label:
            samples.append(metrics.horizontalAdvance(f'Текущий этап: {self._message.stage_label[:60]}') + 24)
        if self._message.params_summary:
            samples.append(metrics.horizontalAdvance(f'Параметры: {self._message.params_summary[:90]}') + 24)
        for step in self._message.steps[:6]:
            step_text = f'• {step.title} · {step.status}' + (f' · {step.message}' if step.message else '')
            samples.append(metrics.horizontalAdvance(step_text[:100]) + 12)
        for artifact in self._message.artifacts[:4]:
            samples.append(metrics.horizontalAdvance(artifact.title[:60]) + 42)
        return max(samples + [320]) + self._layout.contentsMargins().left() + self._layout.contentsMargins().right()

    def set_message(self, message: ScenarioChatMessage) -> None:
        self._message = message
        self._case_id = message.source_case_id
        self.setProperty('tone', message.tone)
        self.setProperty('placement', message.placement)
        self.style().unpolish(self)
        self.style().polish(self)

        self._author.setText(f'{message.author_label} · {message.timestamp_label}')
        self._status_chip.set_status(message.status, message.status_label)
        self._title.setText(message.title)
        self._summary.setText(message.summary)

        if message.stage_label:
            self._stage.setText(f'Текущий этап: {message.stage_label}')
            self._stage.show()
        else:
            self._stage.hide()

        if message.params_summary:
            self._params.setText(f'Параметры: {message.params_summary}')
            self._params.show()
        else:
            self._params.hide()

        self._replace_labels(
            self._steps_layout,
            [
                self._build_step_label(step)
                for step in message.steps
            ],
        )
        self._steps_title.setVisible(bool(message.steps))
        self._steps_host.setVisible(bool(message.steps))

        self._replace_labels(
            self._artifacts_layout,
            [self._build_artifact_button(artifact.title, artifact.path) for artifact in message.artifacts],
        )
        self._artifacts_title.setVisible(bool(message.artifacts))
        self._artifacts_host.setVisible(bool(message.artifacts))

    def _build_step_label(self, step) -> QLabel:
        row = QLabel(f'• {step.title} · {step.status}' + (f' · {step.message}' if step.message else ''))
        row.setObjectName('chatStepLine')
        row.setWordWrap(True)
        return row

    def _build_artifact_button(self, title: str, path: str) -> QPushButton:
        button = QPushButton(title)
        button.setObjectName('feedActionButton')
        button.setToolTip(path)
        button.clicked.connect(lambda checked=False, p=path: self.artifact_open_requested.emit(p))
        return button

    def _replace_labels(self, layout: QVBoxLayout, widgets: list[QWidget]) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        for widget in widgets:
            layout.addWidget(widget)


class ScenarioNoticeBubble(QFrame):
    def __init__(self, message: ScenarioChatMessage, parent=None) -> None:
        super().__init__(parent)
        self._message = message
        self.setObjectName('scenarioNoticeBubble')
        self.setProperty('tone', message.tone)
        self.setProperty('placement', message.placement)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        self._layout = layout
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(4)
        self._meta = QLabel(self)
        self._meta.setObjectName('chatMeta')
        self._meta.setWordWrap(True)
        layout.addWidget(self._meta)
        self._body = QLabel(self)
        self._body.setObjectName('chatMessageBody')
        self._body.setWordWrap(True)
        layout.addWidget(self._body)
        self.set_message(message)

    def suggested_width(self) -> int:
        metrics = QFontMetrics(self._body.font())
        meta_metrics = QFontMetrics(self._meta.font())
        body_width = metrics.horizontalAdvance(self._message.summary[:100]) + 12
        meta_width = meta_metrics.horizontalAdvance(f'{self._message.author_label} · {self._message.timestamp_label}') + 12
        return max(240, body_width, meta_width) + self._layout.contentsMargins().left() + self._layout.contentsMargins().right()

    def set_message(self, message: ScenarioChatMessage) -> None:
        self._message = message
        self.setProperty('tone', message.tone)
        self.setProperty('placement', message.placement)
        self.style().unpolish(self)
        self.style().polish(self)
        self._meta.setText(f'{message.author_label} · {message.timestamp_label}')
        self._body.setText(message.summary)


class ScenarioMessageRow(QWidget):
    clicked = Signal(str)
    artifact_open_requested = Signal(str)

    def __init__(self, message: ScenarioChatMessage, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('scenarioMessageRow')
        self._message = message
        self._bubble: ScenarioCaseBubble | ScenarioNoticeBubble | None = None
        self._avatar = AvatarBadge(
            message.avatar_text,
            actor_kind=message.actor_kind,
            palette_key=message.avatar_palette_key,
            parent=self,
        )
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(18, 2, 18, 2)
        self._layout.setSpacing(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.set_message(message)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        self._apply_bubble_width()
        super().resizeEvent(event)

    def set_message(self, message: ScenarioChatMessage) -> None:
        placement_changed = message.placement != self._message.placement if self._bubble is not None else False
        family_changed = message.message_family != self._message.message_family if self._bubble is not None else False
        self._message = message
        self.setProperty('placement', message.placement)
        self._avatar.set_avatar(
            message.avatar_text,
            actor_kind=message.actor_kind,
            palette_key=message.avatar_palette_key,
        )
        if self._bubble is None or placement_changed or family_changed:
            if self._bubble is not None:
                self._bubble.deleteLater()
            self._bubble = self._create_bubble(message)
            self._rebuild_layout()
        else:
            self._bubble.set_message(message)
        self.style().unpolish(self)
        self.style().polish(self)
        QTimer.singleShot(0, self._apply_bubble_width)

    def bubble_message_id(self) -> str:
        return self._message.message_id

    def _create_bubble(self, message: ScenarioChatMessage) -> ScenarioCaseBubble | ScenarioNoticeBubble:
        if message.message_kind == 'case':
            bubble = ScenarioCaseBubble(message, self)
            bubble.clicked.connect(self.clicked.emit)
            bubble.artifact_open_requested.connect(self.artifact_open_requested.emit)
            return bubble
        return ScenarioNoticeBubble(message, self)

    def _rebuild_layout(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self)
        self._layout.setAlignment(Qt.AlignTop)
        if self._message.placement == 'outgoing':
            self._layout.addStretch(1)
            self._layout.addWidget(self._bubble, 0, Qt.AlignTop | Qt.AlignRight)
            self._layout.addWidget(self._avatar, 0, Qt.AlignTop | Qt.AlignRight)
        else:
            self._layout.addWidget(self._avatar, 0, Qt.AlignTop | Qt.AlignLeft)
            self._layout.addWidget(self._bubble, 0, Qt.AlignTop | Qt.AlignLeft)
            self._layout.addStretch(1)

    def _apply_bubble_width(self) -> None:
        if self._bubble is None:
            return
        contents = self._layout.contentsMargins()
        available = self.width() - contents.left() - contents.right() - self._avatar.width() - self._layout.spacing() - 24
        if available <= 180:
            self._bubble.setFixedWidth(max(160, available))
            return
        if self._message.message_family == 'case':
            min_width = 320
            absolute_max = 760
        else:
            min_width = 220
            absolute_max = 620
        if available < 640:
            ratio = 0.84
        elif available < 900:
            ratio = 0.72
        else:
            ratio = 0.64
        max_width = min(absolute_max, int(available * ratio))
        max_width = max(min_width, max_width)
        suggested_width = self._bubble.suggested_width()
        target_width = max(min_width, min(max_width, suggested_width))
        target_width = min(target_width, max(200, available))
        self._bubble.setFixedWidth(target_width)


class ScenarioChatView(QScrollArea):
    case_selected = Signal(str)
    artifact_open_requested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName('scenarioChatView')
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._rows: dict[str, ScenarioMessageRow] = {}
        self._message_order: list[str] = []
        self._pending_new_count = 0
        self._scroll_target: int | None = None

        self._host = QWidget()
        self._host.setObjectName('scenarioChatHost')
        self._layout = QVBoxLayout(self._host)
        self._layout.setContentsMargins(28, 24, 28, 24)
        self._layout.setSpacing(12)
        self._layout.addStretch(1)
        self.setWidget(self._host)

        self._scroll_animation = QVariantAnimation(self)
        self._scroll_animation.setDuration(180)
        self._scroll_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._scroll_animation.valueChanged.connect(self._apply_scroll_value)
        self.verticalScrollBar().sliderPressed.connect(self._scroll_animation.stop)
        self.verticalScrollBar().valueChanged.connect(self._on_scrollbar_value_changed)

        self._new_messages_button = QPushButton('↓', self.viewport())
        self._new_messages_button.setObjectName('newMessagesButton')
        self._new_messages_button.setToolTip('Прокрутить к новым сообщениям')
        self._new_messages_button.setVisible(False)
        self._new_messages_button.clicked.connect(self.scroll_to_bottom)
        self._position_new_messages_button()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._position_new_messages_button()

    def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
        if event.modifiers() != Qt.NoModifier:
            super().wheelEvent(event)
            return
        delta = event.pixelDelta().y()
        if delta == 0:
            delta = int(event.angleDelta().y() / 120 * 84)
        if delta == 0:
            super().wheelEvent(event)
            return
        bar = self.verticalScrollBar()
        start = bar.value()
        target_seed = self._scroll_target if self._scroll_target is not None else start
        target = max(bar.minimum(), min(bar.maximum(), int(target_seed - delta)))
        self._start_scroll_animation(start, target, duration=120)
        event.accept()

    def set_messages(self, messages: tuple[ScenarioChatMessage, ...], *, reset_view: bool = False) -> None:
        normalized = messages or (
            ScenarioChatMessage(
                message_id='__empty__',
                message_kind='notice',
                tone='info',
                title='Strategy Box готов',
                summary='Выберите сценарий слева или откройте проводник.',
                status_label='Инфо',
                status='info',
                author_label='Система',
                timestamp_label='',
                sort_key='',
                actor_kind='system',
                actor_id='',
                placement='incoming',
                avatar_text='SB',
                avatar_palette_key='system',
                message_family='notice',
            ),
        )
        bar = self.verticalScrollBar()
        previous_value = bar.value()
        was_at_bottom = reset_view or self._is_at_bottom()
        old_ids = set(self._message_order)
        new_ids = [message.message_id for message in normalized]
        new_id_set = set(new_ids)
        created_ids: list[str] = []

        for removed_id in old_ids - new_id_set:
            row = self._rows.pop(removed_id, None)
            if row is not None:
                row.deleteLater()

        for message in normalized:
            row = self._rows.get(message.message_id)
            if row is None:
                row = ScenarioMessageRow(message, self._host)
                row.clicked.connect(self.case_selected.emit)
                row.artifact_open_requested.connect(self.artifact_open_requested.emit)
                self._rows[message.message_id] = row
                created_ids.append(message.message_id)
            else:
                row.set_message(message)

        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(self._host)
        for message in normalized:
            self._layout.addWidget(self._rows[message.message_id], 0, Qt.AlignTop)
        self._layout.addStretch(1)
        self._message_order = new_ids

        def finalize_scroll() -> None:
            if reset_view:
                self._pending_new_count = 0
                self._update_new_messages_button()
                self._scroll_immediately_to_bottom()
                return
            if was_at_bottom:
                self._pending_new_count = 0
                self._update_new_messages_button()
                self._scroll_smoothly_to_bottom()
                return
            self.verticalScrollBar().setValue(min(previous_value, self.verticalScrollBar().maximum()))
            if created_ids and '__empty__' not in created_ids:
                self._pending_new_count += len(created_ids)
            self._update_new_messages_button()

        QTimer.singleShot(0, finalize_scroll)

    def scroll_to_bottom(self) -> None:
        self._pending_new_count = 0
        self._update_new_messages_button()
        self._scroll_smoothly_to_bottom()

    def _scroll_immediately_to_bottom(self) -> None:
        bar = self.verticalScrollBar()
        self._scroll_animation.stop()
        self._scroll_target = None
        bar.setValue(bar.maximum())

    def _scroll_smoothly_to_bottom(self) -> None:
        bar = self.verticalScrollBar()
        self._start_scroll_animation(bar.value(), bar.maximum(), duration=160)

    def _start_scroll_animation(self, start: int, target: int, *, duration: int) -> None:
        if start == target:
            self._scroll_target = None
            self.verticalScrollBar().setValue(target)
            return
        self._scroll_animation.stop()
        self._scroll_target = target
        self._scroll_animation.setDuration(duration)
        self._scroll_animation.setStartValue(start)
        self._scroll_animation.setEndValue(target)
        self._scroll_animation.start()

    def _apply_scroll_value(self, value) -> None:
        self.verticalScrollBar().setValue(int(value))

    def _is_at_bottom(self) -> bool:
        bar = self.verticalScrollBar()
        return bar.value() >= bar.maximum() - 12

    def _on_scrollbar_value_changed(self, value: int) -> None:
        if self._is_at_bottom():
            self._pending_new_count = 0
            self._update_new_messages_button()
        self._position_new_messages_button()
        if self._scroll_target is not None and abs(value - self._scroll_target) <= 2:
            self._scroll_target = None

    def _update_new_messages_button(self) -> None:
        show = self._pending_new_count > 0 and not self._is_at_bottom()
        self._new_messages_button.setVisible(show)
        self._new_messages_button.setToolTip(
            f'Перейти к новым сообщениям ({self._pending_new_count})' if self._pending_new_count else 'Прокрутить к новым сообщениям'
        )
        self._position_new_messages_button()

    def _position_new_messages_button(self) -> None:
        button = self._new_messages_button
        if button is None:
            return
        size = button.sizeHint()
        button.resize(max(44, size.width()), max(44, size.height()))
        x = self.viewport().width() - button.width() - 18
        y = self.viewport().height() - button.height() - 18
        button.move(max(8, x), max(8, y))
        button.raise_()
