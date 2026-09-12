# Copyright (c) 2023 Erwan MATHIEU

import re
import json

from typing import TYPE_CHECKING, Optional, Callable, List, Dict, Any

from datetime import datetime

from UM.Application import Application

if TYPE_CHECKING:
    from PyQt6.QtCore import QByteArray
    from PyQt6.QtNetwork import QNetworkReply

    from ..api.OnshapeApi import OnshapeApi
    from .DocumentsTreeNode import DocumentsTreeNode


class BaseElement:
    """
    Base class for the elements retrieved from the Onshape API
    The elements are organized as such:
    Root > Storage > (Folder) > Document > Workspace > Tab (Part Studio) > Part
    """

    regex_thumbnail_size = re.compile('^([0-9]+)x([0-9]+)$')

    def __init__(self,
                 data: Dict[str, Any],
                 name: str = None,
                 id: str = None,
                 short_desc: Optional[str] = None,
                 last_modified_date: Optional['datetime'] = None,
                 last_modified_by: Optional[str] = None,
                 icon: Optional[str] = None,
                 has_children: bool = True,
                 is_downloadable: bool = False,
                 allow_single_child_shortcut: bool = False,
                 settable_as_default: bool = False,
                 has_thumbnail: bool = False,
                 is_searchable = False):
        """
        Base constructor

        :param name: The user-readable name of the object
        :param id: The unique ID of the object
        :param short_desc: Short basic description of the object (or one of its main properties)
        :param last_modified_date: Object last modification date
        :param last_modified_by: Name of the user at the origin of the last modification
        :param icon: Local URL to an icon of the object
        :param has_children: Indicates whether the object may have children, or if it is a leaf object in the storage tree
        :param is_downloadable: Indicates whether this object may be downloaded, or is just a container
        :param allow_single_child_shortcut: Indicates whether this object may be hidden in case it has a single child, in which case we will
                                            directly navigate to it
        :param settable_as_default: Indicates whether this object can be set as default when loading the storages
        """

        self.name: str = data['name'] if name is None and data is not None else name
        self.id: str = data['id'] if id is None and data is not None and 'id' in data else id
        self.short_desc: Optional[str] = (data['owner']['name'] if ('owner' in data and data['owner'] is not None) else None) if short_desc is None and data is not None else short_desc
        self.last_modified_date: Optional['datetime'] = (datetime.fromisoformat(data['modifiedAt']) if ('modifiedAt' in data and data['modifiedAt'] is not None) else None) if last_modified_date is None and data is not None else last_modified_date
        self.last_modified_by: Optional[str] = (data['modifiedBy']['name'] if ('modifiedBy' in data and data['modifiedBy'] is not None) else None) if last_modified_by is None and data is not None else last_modified_by
        self._has_thumbnail = has_thumbnail
        self.children_url: Optional[str] = (data['treeHref'] if ('treeHref' in data and data['treeHref'] is not None) else data['href'] if 'href' in data else None) if data is not None else None
        self.icon: Optional[str] = icon
        self.has_children: bool = has_children
        self.is_downloadable: bool = is_downloadable
        self.settable_as_default = settable_as_default
        self._allow_single_child_shortcut: bool = allow_single_child_shortcut
        self.is_searchable = is_searchable

    def setAsDefault(self):
        """ Registers this element as being the default root element when opening the Onshape dialog """
        if not self.settable_as_default:
            raise RuntimeError('Element is not settable_as_default')

        element_data = { 'id': self.id, 'name':  self.name, 'href': self.children_url, 'type': type(self).__name__ }
        self._storeDefaultData(element_data)
        Application.getInstance().getPreferences().setValue('plugin_onshape/default_storage', json.dumps(element_data))

    def _storeDefaultData(self, element_data: Dict[str, Any]):
        """
        Method to be overridden by child clases to store extra data to be reloaded when the element is used as the default opened element

        :param element_data: The dictionary in which the element data is stored. Extra keys are to be added, and will be given back when
                             re-constructing the element later
        """
        pass

    def loadChildren(self,
                     api: 'OnshapeApi',
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Starts loading the children of the current object, and immediatly start loading the child
           in case there is a single one and we allow for shortcutting

        :param api The API object to be used to load the children
        :param on_finished Callback function called on success. Receives (children, url_load_next_page, request_body).
        :param on_error Callback function called on communication error
        """
        def shortcut_callback(children: List['DocumentsTreeNode'], url_load_next_page: Optional[str], request_body: Optional[str]):
            if len(children) == 1:
                children[0].element.loadChildren(api, on_finished, on_error)
            else:
                on_finished(children, url_load_next_page, request_body)

        self._loadChildren(api,
                           shortcut_callback if self._allow_single_child_shortcut else on_finished,
                           on_error)

    def searchInside(self,
                     api: 'OnshapeApi',
                     search_query: str,
                     on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                     on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        raise NotImplementedError(f"Element {self.__class__} does not implement the search method")
        """
        Starts a textual search into this element. This method has to be overridden if the is_searchable argument is given as True
        in the constructor.

        :param api The API object to be used to process the search
        :param search_query The string to searched for
        :param on_finished Callback function called on success. Receives (children, url_load_next_page, request_body).
        :param on_error Callback function called on communication error
        """

    def _loadChildren(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[[List['DocumentsTreeNode'], Optional[str], Optional[str]], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """Loads the children of this element"""
        if self.children_url is not None:
            api.loadElements(self.children_url, on_finished, on_error)
        else:
            raise RuntimeError('Element has no children_url and no custom method to load children')

    def hasThumbnail(self) -> bool:
        return self._has_thumbnail

    def loadThumbnail(self,
                      api: 'OnshapeApi',
                      on_finished: Callable[['QByteArray'], None],
                      on_error: Callable[['QNetworkReply', 'QNetworkReply.NetworkError'], None]) -> None:
        """
        Starts loading the remote thumbnail of this element. This method has to be overridden if the has_thumbnail argument is given as True
        in the constructor.

        :param api The API object to be used to process the search
        :param on_finished Callback function called on success. Receives (thumbnail_data).
        :param on_error Callback function called on communication error
        """
        raise RuntimeError('Element declares having a thumbnail, so it should implement the loadThumbnail method')
