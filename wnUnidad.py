#!/usr/bin/env python
# -*- coding: UTF8 	-*-

from GladeConnect import GladeConnect
import gtk
import sys
import dialogos
import debugwindow
import SimpleTree
import ifd
from strSQL.basicas import strSelectUnidad
from psycopg import connect
import completion
import comunes
import treetohtml
import config

(CODIGO,
 DESCRIPCION) = range(2)

schema = config.schema
table = "unidad"

class wnUnidad (GladeConnect):
        
    def __init__(self, conexion=None, padre=None, root="wnUnidad"):
        GladeConnect.__init__(self, "glade/wnUnidad.glade", root)
        self.cnx = conexion
        self.cursor = self.cnx.cursor()
        self.padre = padre
        if padre is None :
            self.wnUnidad.maximize()
            self.frm_padre = self.wnUnidad
        else:
            self.frm_padre = self.padre.frm_padre
            
        self.crea_columnas()
        self.carga_datos()
        
    
    def crea_columnas(self):
        columnas = []
        columnas.append ([CODIGO, "Codigo", int])
        columnas.append ([DESCRIPCION, "Descripcion", str])
        
        self.modelo = gtk.ListStore(int, str)
        SimpleTree.GenColsByModel(self.modelo, columnas, self.treeUnidad)
        self.col_data = [x[0] for x in columnas]
        
    def on_btnImprimir_clicked(self, btn=None):
        t = treetohtml.TreeToHTML(self.treeUnidad,"Unidad", self.col_data)
        t.show()        

        
    def carga_datos(self):
        self.modelo = ifd.ListStoreFromSQL(self.cnx, strSelectUnidad)
        self.treeUnidad.set_model(self.modelo)

    def on_btnAnadir_clicked(self, btn=None, data=None):
        dlg = dlgUnidad(self.cnx, self.frm_padre, False)
        dlg.editando=False
        response = dlg.dlgUnidad.run()
        if response == gtk.RESPONSE_OK:
            self.carga_datos()
    
    def on_btnQuitar_clicked(self, btn=None):
        
        model, it = self.treeUnidad.get_selection().get_selected()
        if model is None or it is None:
            return
        descripcion = model.get_value(it, DESCRIPCION)
        
        if dialogos.yesno("¿Desea eliminar la Unidad <b>%s</b>?\nEsta acción no se puede deshacer\n" % descripcion, self.frm_padre) == gtk.RESPONSE_YES:
            llaves={'descripcion_unidad':descripcion}
            sql = ifd.deleteFromDict(schema + "." + table, llaves)
            try:
                self.cursor.execute(sql, llaves)
                model.remove(it)
            except:
                print sys.exc_info()[1]
                dialogos.error("<b>NO SE PUEDE ELIMINAR</b>\nLa Unidad <b>%s</b>, esta relacionada con un producto"%descripcion)
        
    def on_btnPropiedades_clicked(self, btn=None):

        model, it = self.treeUnidad.get_selection().get_selected()
        if model is None or it is None:
            dialogos.error("Seleccione una Unidad para editar.")
            return
        dlg = dlgUnidad(self.cnx, self.frm_padre, False)
        dlg.entCodigo.set_text(model.get_value(it, CODIGO))
        dlg.entDescripcion.set_text(model.get_value(it, DESCRIPCION))
        
        
        dlg.editando = True
        response = dlg.dlgUnidad.run()
        if response == gtk.RESPONSE_OK:
            self.modelo.clear()
            self.carga_datos()
            
    def on_btnCerrar_clicked(self, btn=None):
        if self.padre is None:
            self.on_exit()
        else:
            self.padre.remove_tab("Unidad")
            
    def on_treeUnidad_row_activated(self, tree=None, path=None, col=None):
        self.on_btnPropiedades_clicked()


class dlgUnidad(GladeConnect):
    def __init__(self, conexion=None, padre=None, editando=None):
        GladeConnect.__init__(self, "glade/wnUnidad.glade", "dlgUnidad")
        self.cnx = conexion
        self.cursor = self.cnx.cursor()
        self.entDescripcion.grab_focus()
        
        self.editando=editando
        self.codigo_tipo_ficha = None
        if self.editando:
            self.entCodigo.set_sensitive(False)
        self.dlgUnidad.show()
    
    def on_btnAceptar_clicked(self, btn=None, date=None, cnx=None):
        if self.entDescripcion.get_text() == "":
            dialogos.error("El campo <b>Descripción Unidad</b> no puede estar vacío")
            return
        
        campos = {}
        llaves = {}
        campos['descripcion_unidad']  = self.entDescripcion.get_text().upper()
        if not self.editando:
            sql = ifd.insertFromDict(schema + "." + table, campos)
            
        else:
            llaves['codigo_unidad'] = self.entCodigo.get_text().upper()
            sql, campos=ifd.updateFromDict(schema + "." + table, campos, llaves)
            
        self.cursor.execute(sql, campos)
        self.dlgUnidad.hide()
        
    def on_btnCancelar_clicked(self, btn=None):
        self.dlgUnidad.hide()
        
if __name__ == '__main__':
    DB = config.DB
    user = config.user
    password = config.password
    host = config.host
    
    cnx = connect(DB + " " + user + " " + password + " " + host )
    cnx.autocommit()
    sys.excepthook = debugwindow.show
    d = wnUnidad(cnx)
    
    gtk.main()
