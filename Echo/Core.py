from collections import deque

from ErisPulse import sdk
from ErisPulse.Core.Bases import BaseModule
from ErisPulse.Core.Event import command, message


class Main(BaseModule):
    def __init__(self):
        self.sdk = sdk
        self.logger = sdk.logger.get_child("Echo")
        self._history = {}
        self._config = self._load_config()

    @staticmethod
    def get_load_strategy():
        from ErisPulse.loaders import ModuleLoadStrategy
        return ModuleLoadStrategy(
            lazy_load=False,
            priority=0,
        )

    async def on_load(self, event):
        max_history = self._config.get("max_history", 10)

        @message.on_message()
        async def _track_message(evt):
            key = self._get_conv_key(evt)
            if key not in self._history:
                self._history[key] = deque(maxlen=max_history)
            msg_id = evt.get("message_id") or evt.get_id()
            if not msg_id:
                return
            self._history[key].append((msg_id, list(evt.get_message())))

        @command("echo", help="回显消息内容")
        async def _echo_handler(evt):
            segments = evt.get_message()

            reply_msg_id = None
            for seg in segments:
                if seg.get("type") == "reply":
                    reply_msg_id = seg.get("data", {}).get("message_id")
                    break

            if reply_msg_id:
                key = self._get_conv_key(evt)
                history = self._history.get(key, deque())
                for msg_id, msg_segs in history:
                    if msg_id == reply_msg_id:
                        if msg_segs:
                            await evt.reply_ob12(msg_segs)
                        else:
                            await evt.reply("该消息没有可回显的内容")
                        return
                await evt.reply(
                    "该消息太早，无法回显（仅支持最近{}条消息）".format(max_history)
                )
                return

            args = evt.get_command_args()
            if args:
                args = [a for a in args if a.strip()]
            if not args:
                args = None

            media_segments = []
            for seg in segments:
                seg_type = seg.get("type")
                if seg_type in ("text", "reply"):
                    continue
                media_segments.append(seg)

            if args and media_segments:
                text_seg = {"type": "text", "data": {"text": " ".join(args)}}
                await evt.reply_ob12([text_seg] + media_segments)
                return

            if args:
                await evt.reply(" ".join(args))
                return

            if media_segments:
                await evt.reply_ob12(media_segments)
                return

            await evt.reply("用法: /echo <内容> 或回复一条消息使用 /echo")

        self.logger.info("Echo 模块已加载")

    async def on_unload(self, event):
        self._history.clear()
        self.logger.info("Echo 模块已卸载")

    def _get_conv_key(self, event):
        platform = event.get_platform()
        detail_type = event.get_detail_type()
        if detail_type == "group":
            target = event.get_group_id()
        else:
            target = event.get_user_id()
        return (platform, detail_type, target)

    def _load_config(self):
        config = self.sdk.config.getConfig("Echo")
        if not config:
            default_config = {
                "max_history": 10,
            }
            self.sdk.config.setConfig("Echo", default_config, immediate=True)
            return default_config
        return config
