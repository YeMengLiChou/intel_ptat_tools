from abc import ABC, abstractmethod


class EventObserver(ABC):
    @abstractmethod
    def on_event(self, *args):
        pass

    @abstractmethod
    def event_name(self) -> str:
        pass


class EventDispatcher:
    def __init__(self) -> None:
        self.observers: dict[str, list[EventObserver]] = dict()

    def register_observer(self, observer: EventObserver):
        event_name = observer.event_name()

        if event_name not in self.observers:
            self.observers[event_name] = [observer]
        else:
            self.observers[event_name].append(observer)

    def unregister_observer(self, observer: EventObserver):
        event_name = observer.event_name()
        if event_name in self.observers:
            self.observers[event_name].remove(observer)

    def dispatch_event(self, event_name: str, *event):
        print("dispatch [{}]: {}".format(event_name, event))
        if event_name in self.observers:
            for observer in self.observers[event_name]:
                observer.on_event(*event)
