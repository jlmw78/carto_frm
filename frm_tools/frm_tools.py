# -*- coding: utf-8 -*-
"""
/***************************************************************************
 frmTools
                                 A QGIS plugin
 conjunto de herramientas utiles
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-28
        git sha              : $Format:%H$
        copyright            : (C) 2021 by jlmw78
        email                : j@j.j
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   Este programa es software libre; puede redistribuirlo y/o modificarlo *
 *   bajo los términos de la Licencia Pública General de GNU publicada por *
 *   la Fundación de Software Libre.                                       *
 *   la Free Software Foundation; ya sea la versión 2 de la Licencia, o    *
 *   (a su elección) cualquier versión posterior.                          * 
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .frm_tools_dialog import frmToolsDialog
import os
import os.path
from qgis import processing


class frmTools:
    """QGIS Plugin Implementation."""


    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'frmTools_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&herraientas carto frm')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None
        
        # genero la barra de herramientas
        self.toolbar = self.iface.addToolBar(u'CartoTools')
        self.toolbar.setObjectName(u'CartoTools')        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('frmTools', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.toolbar.addAction(action) # agrega icono al la barra

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path1 = self.plugin_dir+'/icons/icon_limitipos2.png'
        self.add_action(
            icon_path1,
            text=self.tr(u'Limitipo'),
            callback=self.runtool1, #ejecuta el def runtool1
            parent=self.iface.mainWindow())
            
        icon_path3 = self.plugin_dir+'/icons/icon_f_r2.png'
        self.add_action(
            icon_path3,
            text=self.tr(u'fraccion y radio'),
            callback=self.runtool3, #ejecuta el def runtool2
            parent=self.iface.mainWindow())

        icon_path2 = self.plugin_dir+'/icons/icon_mza2.png'
        self.add_action(
            icon_path2,
            text=self.tr(u'genera Manzanero'),
            callback=self.runtool2, #ejecuta el def runtool3
            parent=self.iface.mainWindow())
 
        icon_path4 = self.plugin_dir+'/icons/icon_izq_der.png'
        self.add_action(
            icon_path4,
            text=self.tr(u'calcula mzai y mzad'),
            callback=self.runtool4, #ejecuta el def runtool3
            parent=self.iface.mainWindow())   
        
        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&herraientas carto frm'),
                action)
            self.iface.removeToolBarIcon(action)            
            
    def runtool1(self):
         # lanza el proceso limitipos
         processing.execAlgorithmDialog("model:limitipo", {})

                  
    def runtool2(self):
         # lanza el proceso manzanero
         processing.execAlgorithmDialog("model:genera_manzanero", {})

    def runtool3(self):
         # lanza el proceso radio y fraccion  
         processing.execAlgorithmDialog("model:radio y fraccion", {})
         
    def runtool4(self):
         # lanza el proceso mza izq der  
         processing.execAlgorithmDialog("model:mza_izq_der", {})


