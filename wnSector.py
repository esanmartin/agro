#!/usr/bin/env python
# -*- coding: UTF8 	-*-

from GladeConnect import GladeConnect
import gtk
import sys
import dialogos
import debugwindow
import SimpleTree
import ifd
from strSQL.basicas import strSelectSector
from psycopg import connect
import completion
import comunes
import treetohtml
import config

(CODIGO_SECTOR,
 DESCRIPCION) = range(2)

schema = config.schema
table = "sector"

class wnSector (GladeConnect):
    def __init__(self, conexion=None, padre=None, root="wnSector"):
        GladeConnect.__init__(self, "glade/wnSector.glade", root)
        self.cnx = conexion
        self.cursor = self.cnx.cursor()
        self.padre = padre
        if padre is None :
            self.wnSector.maximize()
            self.frm_padre = self.wnSector
        else:
            self.frm_padre = padre.frm_padre

        self.crea_columnas()
        self.carga_datos()

    def crea_columnas(self):
        columnas = []
        columnas.append ([CODIGO_SECTOR, "Sector", "str"])
        columnas.append ([DESCRIPCION, "Descripcion", "str"])

        self.modelo = gtk.ListStore(*(2*[str]))
        SimpleTree.GenColsByModel(self.modelo, columnas, self.treeSector)
        self.col_data = [x[0] for x in columnas]

    def on_btnImprimir_clicked(self, btn=None):
        t = treetohtml.TreeToHTML(self.treeSector,"Sector", self.col_data)
        t.show()
    def carga_datos(self):
        self.modelo = ifd.ListStoreFromSQL(self.cnx, strSelectSector)
        self.treeSector.set_model(self.modelo)

    def on_btnAnadir_clicked(self, btn=None, data=None):
        dlg = dlgSector(self.cnx, self.frm_padre, False)
        dlg.editando=False
        response = dlg.dlgSector.run()
        if response == gtk.RESPONSE_OK:
            self.carga_datos()

    def on_btnQuitar_clicked(self, btn=None):
        selection = self.treeSector.get_selection()
        model, it = selection.get_selected()
        if model is None or it is None:
            return

        codigo_sector = model.get_value(it, CODIGO_SECTOR)
        descripcion = model.get_value(it, DESCRIPCION)

        if dialogos.yesno("¿Desea eliminar el Sector <b>%s</b>?\nEsta acción no se puede deshacer\n" % descripcion, self.frm_padre) == gtk.RESPONSE_YES:
            try:
                llaves = {'codigo_sector':codigo_sector}
                sql = ifd.deleteFromDict(config.schema + '.' + table, llaves)
                self.cursor.execute(sql, llaves)
                model.remove(it)
            except:
                 print sys.exc_info()[1]
                 dialogos.error("<b>NO SE PUEDE ELIMINAR</b>\nExisten datos relacionados con:\n<b>%s</b>"%descripcion)

    def on_btnPropiedades_clicked(self, btn=None):
        model, it = self.treeSector.get_selection().get_selected()
        if model is None or it is None:
            dialogos.error("Seleccione un Sector para editar.")
            return
        dlg = dlgSector(self.cnx, self.frm_padre, False)
        dlg.entDescripcion.set_text(model.get_value(it, DESCRIPCION))
        dlg.entCodigo.set_text(model.get_value(it, CODIGO_SECTOR))
        dlg.editando = (True)
        response = dlg.dlgSector.run()
        if response == gtk.RESPONSE_OK:
            self.modelo.clear()
            self.carga_datos()

    def on_btnCerrar_clicked(self, btn=None):
        if self.padre is None:
            self.on_exit()
        else:
            self.padre.remove_tab("Sector")

    def on_treeSector_row_activated(self, tree=None, path=None, col=None):
        self.on_btnPropiedades_clicked()


class dlgSector(GladeConnect):
    def __init__(self, conexion=None, padre=None, editando=None):
        GladeConnect.__init__(self, "glade/wnSector.glade", "dlgSector")
        self.cnx = conexion
        self.cursor = self.cnx.cursor()
        self.editando=editando
        if self.editando:
            self.entCodigo.set_sensitive(False)

        self.dlgSector.show()

    def sel_cultivo(self, completion, model, iter):
        self.codigo_cultivo = model.get_value(iter, 1)

    def on_btnAceptar_clicked(self, btn=None, date=None, cnx=None):

        if self.entDescripcion.get_text() == "":
            dialogos.error("El campo <b>Descripción Sector</b> no puede estar vacío")
            return

        campos = {}
        llaves = {}
        campos['descripcion_sector']  = self.entDescripcion.get_text().upper()

        if not self.editando:
            sql = ifd.insertFromDict(schema + "." + table, campos)
        else:
            llaves['codigo_sector'] = self.entCodigo.get_text()
            sql, campos=ifd.updateFromDict(schema + "." + table, campos, llaves)

        try:
            self.cursor.execute(sql, campos)
            self.dlgSector.hide()
        except:
            print sys.exc_info()[1]


    def on_btnCancelar_clicked(self, btn=None):
        self.dlgSector.hide()

if __name__ == '__main__':
    DB = config.DB
    user = config.user
    password = config.password
    host = config.host

    cnx = connect(DB + " " + user + " " + password + " " + host )
    cnx.autocommit()
    sys.excepthook = debugwindow.show
    d = wnSector(cnx)

    gtk.main()
