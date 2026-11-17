"""
Analizador de Lenguaje Lua (Léxico, Sintáctico y Semántico)
Interfaz Gráfica construida con Tkinter.
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Importación de los módulos backend desarrollados por el equipo
try:
    import lexer
    from semantico import AnalizadorSemantico
    import sintactico
except ImportError as e:
    print(f"Error al importar módulos del compilador: {e}")


class AnalizadorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Analizador de Lenguaje - Lua")
        self.root.geometry("1100x680")
        self.root.minsize(900, 550)

        # Estado del tema (True = Dark Mode, False = Light Mode)
        self.dark_mode = True

        # Paleta de Colores
        self.COLORES = {
            # General
            "dark_bg": "#1E1E2E",
            "dark_fg": "#CDD6F4",
            "light_bg": "#F5F5F7",
            "light_fg": "#1E1E2E",
            # Bordes del editor (fondo siempre blanco)
            "border_dark": "#FFFFFF",   # Borde blanco para resaltar en fondo oscuro
            "border_light": "#000000",  # Borde negro para delimitar en fondo claro
            # Botones inferiores
            "btn_enviar": "#2E7D32",    # Verde
            "btn_enviar_fg": "#FFFFFF",
            "btn_borrar": "#C62828",    # Rojo
            "btn_borrar_fg": "#FFFFFF",
            "btn_cargar": "#F57F17",    # Amarillo / Ámbar
            "btn_cargar_fg": "#FFFFFF",
            # Cuadro de resultados según estado
            "res_neutral_bg": "#FAFAFA",
            "res_neutral_fg": "#212121",
            "res_exito_bg": "#E8F5E9",   # Verde pastel
            "res_exito_fg": "#1B5E20",
            "res_error_bg": "#FFEBEE",   # Rojo pálido
            "res_error_fg": "#B71C1C",
        }

        self._crear_interfaz()
        self._aplicar_tema()

    def _crear_interfaz(self):
        # -------------------------------------------------------------------
        # 1. Encabezado Superior (Título + Botón de Tema)
        # -------------------------------------------------------------------
        self.frame_header = tk.Frame(self.root, pady=10, padx=15)
        self.frame_header.pack(fill=tk.X)

        self.lbl_titulo = tk.Label(
            self.frame_header,
            text="Analizador de Lenguaje",
            font=("Segoe UI", 16, "bold"),
        )
        self.lbl_titulo.pack(side=tk.LEFT)

        self.btn_tema = tk.Button(
            self.frame_header,
            text="🌙 Modo Oscuro",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._alternar_tema,
        )
        self.btn_tema.pack(side=tk.RIGHT)

        # -------------------------------------------------------------------
        # 2. Contenedor Principal (2 Columnas del Mismo Tamaño)
        # -------------------------------------------------------------------
        self.frame_cuerpo = tk.Frame(self.root, padx=15, pady=5)
        self.frame_cuerpo.pack(fill=tk.BOTH, expand=True)

        self.frame_cuerpo.columnconfigure(0, weight=1)
        self.frame_cuerpo.columnconfigure(1, weight=1)
        self.frame_cuerpo.rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: Editor de Código ---
        self.frame_editor_container = tk.Frame(self.frame_cuerpo)
        self.frame_editor_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lbl_edicion = tk.Label(
            self.frame_editor_container,
            text="Código Fuente (Lua):",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        lbl_edicion.pack(fill=tk.X, pady=(0, 5))

        # Frame contenedor que simula el borde dinámico del editor
        self.frame_borde_editor = tk.Frame(self.frame_editor_container, bd=2)
        self.frame_borde_editor.pack(fill=tk.BOTH, expand=True)

        self.txt_editor = tk.Text(
            self.frame_borde_editor,
            wrap=tk.NONE,
            font=("Consolas", 11),
            bg="#FFFFFF",      # Fondo SIEMPRE blanco
            fg="#000000",      # Texto negro
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=5,
        )
        scroll_editor_y = tk.Scrollbar(self.frame_borde_editor, command=self.txt_editor.yview)
        self.txt_editor.configure(yscrollcommand=scroll_editor_y.set)

        scroll_editor_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- PANEL DERECHO: Resultados del Análisis ---
        self.frame_res_container = tk.Frame(self.frame_cuerpo)
        self.frame_res_container.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_resultados = tk.Label(
            self.frame_res_container,
            text="Resultados del Análisis:",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        lbl_resultados.pack(fill=tk.X, pady=(0, 5))

        self.frame_borde_res = tk.Frame(self.frame_res_container, bd=1, bg="#CCCCCC")
        self.frame_borde_res.pack(fill=tk.BOTH, expand=True)

        self.txt_resultados = tk.Text(
            self.frame_borde_res,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,  # Lectura sola por defecto
            relief=tk.FLAT,
            bd=5,
        )
        scroll_res_y = tk.Scrollbar(self.frame_borde_res, command=self.txt_resultados.yview)
        self.txt_resultados.configure(yscrollcommand=scroll_res_y.set)

        scroll_res_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_resultados.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------------
        # 3. Barra Inferior de Botones (Alineada a la Izquierda)
        # -------------------------------------------------------------------
        self.frame_botones = tk.Frame(self.root, padx=15, pady=12)
        self.frame_botones.pack(fill=tk.X)

        # Botón Enviar (Verde)
        self.btn_enviar = tk.Button(
            self.frame_botones,
            text="▶ Enviar",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORES["btn_enviar"],
            fg=self.COLORES["btn_enviar_fg"],
            activebackground="#1B5E20",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._evaluar_codigo,
        )
        self.btn_enviar.pack(side=tk.LEFT, padx=(0, 10))

        # Botón Borrar (Rojo)
        self.btn_borrar = tk.Button(
            self.frame_botones,
            text="🗑 Borrar",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORES["btn_borrar"],
            fg=self.COLORES["btn_borrar_fg"],
            activebackground="#8E0000",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._borrar_editor,
        )
        self.btn_borrar.pack(side=tk.LEFT, padx=(0, 10))

        # Botón Cargar (.txt) (Amarillo)
        self.btn_cargar = tk.Button(
            self.frame_botones,
            text="📂 Cargar (.txt)",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLORES["btn_cargar"],
            fg=self.COLORES["btn_cargar_fg"],
            activebackground="#F57F17",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._cargar_archivo,
        )
        self.btn_cargar.pack(side=tk.LEFT)

    # -----------------------------------------------------------------------
    # Lógica de Cambio de Tema (Modo Oscuro / Claro)
    # -----------------------------------------------------------------------
    def _alternar_tema(self):
        self.dark_mode = not self.dark_mode
        self._aplicar_tema()

    def _aplicar_tema(self):
        if self.dark_mode:
            bg_gen = self.COLORES["dark_bg"]
            fg_gen = self.COLORES["dark_fg"]
            borde_editor = self.COLORES["border_dark"]
            self.btn_tema.config(text="☀️ Modo Claro", bg="#313244", fg="#CDD6F4")
        else:
            bg_gen = self.COLORES["light_bg"]
            fg_gen = self.COLORES["light_fg"]
            borde_editor = self.COLORES["border_light"]
            self.btn_tema.config(text="🌙 Modo Oscuro", bg="#E0E0E0", fg="#1E1E2E")

        # Aplicar colores generales a ventanas y contenedores
        self.root.config(bg=bg_gen)
        self.frame_header.config(bg=bg_gen)
        self.lbl_titulo.config(bg=bg_gen, fg=fg_gen)
        self.frame_cuerpo.config(bg=bg_gen)
        self.frame_editor_container.config(bg=bg_gen)
        self.frame_res_container.config(bg=bg_gen)
        self.frame_botones.config(bg=bg_gen)

        # Actualizar borde dinámico del cuadro de texto (el fondo de txt_editor sigue blanco)
        self.frame_borde_editor.config(bg=borde_editor)

        # Actualizar labels secundarios
        for widget in (self.frame_editor_container, self.frame_res_container):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=bg_gen, fg=fg_gen)

    # -----------------------------------------------------------------------
    # Acciones de los Botones
    # -----------------------------------------------------------------------
    def _borrar_editor(self):
        """Limpia el cuadro de texto editable y restablece el panel de resultados."""
        self.txt_editor.delete("1.0", tk.END)
        self._set_panel_resultados("", estado="neutral")

    def _cargar_archivo(self):
        """Abre un diálogo para cargar código desde un archivo de texto o .lua."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de código",
            filetypes=[("Archivos de Texto / Lua", "*.txt *.lua"), ("Todos los archivos", "*.*")],
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.txt_editor.delete("1.0", tk.END)
                self.txt_editor.insert("1.0", contenido)
            except Exception as e:
                messagebox.showerror("Error de lectura", f"No se pudo leer el archivo:\n{e}")

    # -----------------------------------------------------------------------
    # Evaluación Secuencial (Léxico -> Sintáctico -> Semántico)
    # -----------------------------------------------------------------------
    def _evaluar_codigo(self):
        codigo = self.txt_editor.get("1.0", tk.END).rstrip("\n")

        # Si el recuadro está totalmente vacío, no hace nada
        if not codigo.strip():
            return

        lineas_codigo = codigo.split("\n")

        # --- 1. EVALUACIÓN LÉXICA ---
        lexer.lexer.lineno = 1
        lexer.lexer.errores = []
        lexer.lexer.input(codigo)

        tokens_reconocidos = []
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            tokens_reconocidos.append(tok)

        if lexer.lexer.errores:
            msg_raw = lexer.lexer.errores[0]
            linea_num, fragmento = self._extraer_info_error(msg_raw, lineas_codigo)
            detalle = (
                f"❌ ERROR LÉXICO DETECTADO\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Línea: {linea_num}\n"
                f"• Fragmento erróneo: \"{fragmento}\"\n"
                f"• Descripción: {msg_raw}"
            )
            self._set_panel_resultados(detalle, estado="error")
            return

        # --- 2. EVALUACIÓN SINTÁCTICA ---
        try:
            ast = sintactico.parse(codigo)
        except sintactico.ParseError as error:
            msg_raw = str(error).splitlines()[0] if str(error) else "Error sintáctico desconocido"
            linea_num, fragmento = self._extraer_info_error(msg_raw, lineas_codigo)
            detalle = (
                f"❌ ERROR SINTÁCTICO DETECTADO\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Línea: {linea_num}\n"
                f"• Fragmento erróneo: \"{fragmento}\"\n"
                f"• Descripción: {msg_raw}"
            )
            self._set_panel_resultados(detalle, estado="error")
            return
        except Exception as ex:
            self._set_panel_resultados(f"❌ ERROR SINTÁCTICO GENERAL:\n{ex}", estado="error")
            return

        # --- 3. EVALUACIÓN SEMÁNTICA ---
        analizador_sem = AnalizadorSemantico()
        errores_semanticos = analizador_sem.analizar(ast)

        if errores_semanticos:
            primer_error = errores_semanticos[0]
            linea_num = primer_error.linea
            fragmento = (
                lineas_codigo[linea_num - 1].strip()
                if 1 <= linea_num <= len(lineas_codigo)
                else "Desconocido"
            )
            detalle = (
                f"❌ ERROR SEMÁNTICO DETECTADO\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Regla violada: [{primer_error.regla}]\n"
                f"• Línea: {linea_num}\n"
                f"• Fragmento erróneo: \"{fragmento}\"\n"
                f"• Descripción: {primer_error.mensaje}"
            )
            self._set_panel_resultados(detalle, estado="error")
            return

        # --- 4. ÉXITO (CÓDIGO VÁLIDO) ---
        salida_exito = (
            f"✔ ANÁLISIS COMPLETADO SIN ERRORES\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• Estado: Código Lua Léxica, Sintáctica y Semánticamente VÁLIDO.\n"
            f"• Instrucciones AST reconocidas: {len(ast)}\n"
            f"• Tokens procesados: {len(tokens_reconocidos)}\n\n"
            f"--- ESTRUCTURA AST RECONOCIDA ---\n"
        )
        for i, stmt in enumerate(ast, 1):
            salida_exito += f"[{i}] {stmt}\n"

        self._set_panel_resultados(salida_exito, estado="exito")

    # -----------------------------------------------------------------------
    # Métodos Auxiliares
    # -----------------------------------------------------------------------
    def _extraer_info_error(self, mensaje_error: str, lineas_codigo: list[str]) -> tuple[int, str]:
        """Extrae el número de línea y la porción de código donde ocurrió el error."""
        match_linea = re.search(r"línea\s+(\d+)", mensaje_error, re.IGNORECASE)
        if match_linea:
            linea_num = int(match_linea.group(1))
            fragmento = (
                lineas_codigo[linea_num - 1].strip()
                if 1 <= linea_num <= len(lineas_codigo)
                else "Código inaccesible"
            )
            return linea_num, fragmento
        return 1, lineas_codigo[0].strip() if lineas_codigo else "Código vacío"

    def _set_panel_resultados(self, texto: str, estado: str = "neutral"):
        """Actualiza el panel derecho con el texto, color de fondo y tipo de respuesta."""
        self.txt_resultados.config(state=tk.NORMAL)
        self.txt_resultados.delete("1.0", tk.END)
        self.txt_resultados.insert("1.0", texto)

        if estado == "error":
            bg = self.COLORES["res_error_bg"]
            fg = self.COLORES["res_error_fg"]
        elif estado == "exito":
            bg = self.COLORES["res_exito_bg"]
            fg = self.COLORES["res_exito_fg"]
        else:
            bg = self.COLORES["res_neutral_bg"]
            fg = self.COLORES["res_neutral_fg"]

        self.txt_resultados.config(bg=bg, fg=fg, state=tk.DISABLED)


# ---------------------------------------------------------------------------
# Punto de Entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app_root = tk.Tk()
    app = AnalizadorGUI(app_root)
    app_root.mainloop()