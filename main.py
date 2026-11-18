"""
Analizador de Lenguaje Lua (Léxico, Sintáctico y Semántico)
Interfaz Gráfica construida con Tkinter (Diseño IDE Autoadaptable y Responsive).
"""

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

# Importación de los módulos backend desarrollados por el equipo
try:
    import lexer
    import sintactico
    from semantico import AnalizadorSemantico
except ImportError as e:
    print(f"Error al importar módulos del compilador: {e}")


class TextWithLineNumbers(tk.Frame):
    """Editor de código tipo IDE con numeración alineada milimétricamente y scroll horizontal."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Mismo estilo exacto para garantizar sincronización de líneas
        FONT_CONFIG = ("Consolas", 10)
        PAD_Y = 4

        # Gutter (Números de línea)
        self.linenumbers = tk.Text(
            self,
            width=4,
            padx=4,
            pady=PAD_Y,
            takefocus=0,
            border=0,
            bg="#E0E0E0",
            fg="#666666",
            font=FONT_CONFIG,
            state=tk.DISABLED,
            wrap=tk.NONE,
            spacing1=0,
            spacing2=0,
            spacing3=0,
        )
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        # Separador visual vertical
        self.separador = tk.Frame(self, width=1, bg="#CCCCCC")
        self.separador.pack(side=tk.LEFT, fill=tk.Y)

        # Contenedor derecho para el texto y el scroll horizontal
        self.frame_text_area = tk.Frame(self)
        self.frame_text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Cuadro de edición de código (Fondo SIEMPRE blanco)
        self.text = tk.Text(
            self.frame_text_area,
            wrap=tk.NONE,
            font=FONT_CONFIG,
            padx=6,
            pady=PAD_Y,
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            relief=tk.FLAT,
            bd=0,
            spacing1=0,
            spacing2=0,
            spacing3=0,
        )
        
        # Scrollbars
        self.scrollbar_y = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._on_scroll_y)
        self.scrollbar_x = tk.Scrollbar(self.frame_text_area, orient=tk.HORIZONTAL, command=self.text.xview)

        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.text.config(
            yscrollcommand=self._on_text_scroll_y,
            xscrollcommand=self.scrollbar_x.set,
        )

        # Eventos para actualizar la numeración en tiempo real
        self.text.bind("<KeyRelease>", self.update_line_numbers)
        self.text.bind("<Configure>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.update_line_numbers)

        # Resaltado de líneas con error (Fondo rojo claro)
        self.text.tag_configure("error_line", background="#FFCDD2")

    def _on_scroll_y(self, *args):
        self.text.yview(*args)
        self.linenumbers.yview(*args)

    def _on_text_scroll_y(self, *args):
        self.scrollbar_y.set(*args)
        self.linenumbers.yview_moveto(args[0])

    def update_line_numbers(self, event=None):
        line_count = self.text.get("1.0", "end-1c").count("\n") + 1
        lines_string = "\n".join(str(i) for i in range(1, line_count + 1))

        self.linenumbers.config(state=tk.NORMAL)
        self.linenumbers.delete("1.0", tk.END)
        self.linenumbers.insert("1.0", lines_string)
        self.linenumbers.config(state=tk.DISABLED)
        self.linenumbers.yview_moveto(self.text.yview()[0])

    def resaltar_lineas_error(self, lineas: set[int]):
        """Limpia resaltados anteriores y pinta las líneas indicadas."""
        self.text.tag_remove("error_line", "1.0", tk.END)
        for num_linea in lineas:
            self.text.tag_add("error_line", f"{num_linea}.0", f"{num_linea}.end")


class AnalizadorGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Analizador de Lenguaje - Lua")
        self.root.geometry("1100x680")
        self.root.minsize(850, 500)

        self.dark_mode = True
        self.modo_analisis = "completo"

        # Resultados de la última evaluación
        self.last_lex_tokens = []
        self.last_lex_errors = []
        self.last_ast = None
        self.last_syn_errors = []
        self.last_sem_errors = []
        self.last_lines_code = []

        self.COLORES = {
            "dark_bg": "#1E1E2E",
            "dark_fg": "#CDD6F4",
            "light_bg": "#F5F5F7",
            "light_fg": "#1E1E2E",
            "border_dark": "#FFFFFF",
            "border_light": "#000000",
            "btn_enviar": "#2E7D32",
            "btn_borrar": "#C62828",
            "btn_cargar": "#F57F17",
            "res_neutral_bg": "#FAFAFA",
            "res_neutral_fg": "#212121",
            "res_exito_bg": "#E8F5E9",
            "res_exito_fg": "#1B5E20",
            "res_error_bg": "#FFEBEE",
            "res_error_fg": "#B71C1C",
        }

        # Configuración responsive del root
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self._crear_interfaz()
        self._aplicar_tema()

    def _crear_interfaz(self):
        # Contenedor Principal Flexible
        self.main_container = tk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky="nsew")

        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)  # El cuerpo se expande verticalmente

        # -------------------------------------------------------------------
        # 1. Encabezado Superior
        # -------------------------------------------------------------------
        self.frame_header = tk.Frame(self.main_container, pady=8, padx=15)
        self.frame_header.grid(row=0, column=0, sticky="ew")

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
        # 2. Contenedor Central Autoadaptable (2 Columnas de igual peso)
        # -------------------------------------------------------------------
        self.frame_cuerpo = tk.Frame(self.main_container, padx=15, pady=5)
        self.frame_cuerpo.grid(row=1, column=0, sticky="nsew")

        self.frame_cuerpo.columnconfigure(0, weight=1)
        self.frame_cuerpo.columnconfigure(1, weight=1)
        self.frame_cuerpo.rowconfigure(0, weight=1)

        # --- PANEL IZQUIERDO: Editor IDE ---
        self.frame_editor_container = tk.Frame(self.frame_cuerpo)
        self.frame_editor_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.frame_editor_container.rowconfigure(1, weight=1)
        self.frame_editor_container.columnconfigure(0, weight=1)

        lbl_edicion = tk.Label(
            self.frame_editor_container,
            text="Código Fuente (Lua):",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        lbl_edicion.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.frame_borde_editor = tk.Frame(self.frame_editor_container, bd=2)
        self.frame_borde_editor.grid(row=1, column=0, sticky="nsew")

        self.editor_ide = TextWithLineNumbers(self.frame_borde_editor)
        self.editor_ide.pack(fill=tk.BOTH, expand=True)

        # --- PANEL DERECHO: Sub-paneles Autoadaptables ---
        self.frame_res_container = tk.Frame(self.frame_cuerpo)
        self.frame_res_container.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.frame_res_container.columnconfigure(0, weight=1)
        self.frame_res_container.rowconfigure(1, weight=1)  # Sub-panel 1 expandible
        self.frame_res_container.rowconfigure(3, weight=1)  # Sub-panel 2 expandible

        # Sub-panel 1: Resultado por Fase
        self.lbl_fase_titulo = tk.Label(
            self.frame_res_container,
            text="Resultado por Fase:",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.lbl_fase_titulo.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        self.frame_borde_fase = tk.Frame(self.frame_res_container, bd=1, bg="#CCCCCC")
        self.frame_borde_fase.grid(row=1, column=0, sticky="nsew", pady=(0, 8))

        self.txt_fase = tk.Text(
            self.frame_borde_fase,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=4,
        )
        scroll_fase = tk.Scrollbar(self.frame_borde_fase, command=self.txt_fase.yview)
        self.txt_fase.configure(yscrollcommand=scroll_fase.set)
        scroll_fase.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_fase.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sub-panel 2: Errores Encontrados
        self.lbl_errores_titulo = tk.Label(
            self.frame_res_container,
            text="Errores Encontrados:",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.lbl_errores_titulo.grid(row=2, column=0, sticky="ew", pady=(0, 2))

        self.frame_borde_errores = tk.Frame(self.frame_res_container, bd=1, bg="#CCCCCC")
        self.frame_borde_errores.grid(row=3, column=0, sticky="nsew")

        self.txt_errores = tk.Text(
            self.frame_borde_errores,
            wrap=tk.WORD,
            font=("Consolas", 10),
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=4,
        )
        scroll_err = tk.Scrollbar(self.frame_borde_errores, command=self.txt_errores.yview)
        self.txt_errores.configure(yscrollcommand=scroll_err.set)
        scroll_err.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_errores.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # -------------------------------------------------------------------
        # 3. Fila Única de Botones Inferiores (Al Mismo Nivel)
        # -------------------------------------------------------------------
        self.frame_botones = tk.Frame(self.main_container, padx=15, pady=10)
        self.frame_botones.grid(row=2, column=0, sticky="ew")

        # Izquierda (Debajo del Editor)
        self.frame_btn_left = tk.Frame(self.frame_botones)
        self.frame_btn_left.pack(side=tk.LEFT)

        self.btn_enviar = tk.Button(
            self.frame_btn_left,
            text="▶ Enviar",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORES["btn_enviar"],
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._evaluar_codigo,
        )
        self.btn_enviar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_borrar = tk.Button(
            self.frame_btn_left,
            text="🗑 Borrar",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORES["btn_borrar"],
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._borrar_editor,
        )
        self.btn_borrar.pack(side=tk.LEFT, padx=(0, 6))

        self.btn_cargar = tk.Button(
            self.frame_btn_left,
            text="📂 Cargar Archivo",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLORES["btn_cargar"],
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=14,
            pady=5,
            cursor="hand2",
            command=self._cargar_archivo,
        )
        self.btn_cargar.pack(side=tk.LEFT)

        # Derecha (Debajo de los Resultados)
        self.frame_btn_right = tk.Frame(self.frame_botones)
        self.frame_btn_right.pack(side=tk.RIGHT)

        self.btns_modo = {}
        modos = [
            ("completo", "Análisis completo"),
            ("lexico", "Léxico"),
            ("sintactico", "Sintáctico"),
            ("semantico", "Semántico"),
        ]

        for clave, texto in modos:
            btn = tk.Button(
                self.frame_btn_right,
                text=texto,
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=5,
                cursor="hand2",
                command=lambda m=clave: self._cambiar_modo_analisis(m),
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.btns_modo[clave] = btn

        self._actualizar_estilo_botones_modo()

    # -----------------------------------------------------------------------
    # Gestión de Temas y Modos
    # -----------------------------------------------------------------------
    def _alternar_tema(self):
        self.dark_mode = not self.dark_mode
        self._aplicar_tema()

    def _aplicar_tema(self):
        if self.dark_mode:
            bg_gen = self.COLORES["dark_bg"]
            fg_gen = self.COLORES["dark_fg"]
            borde_editor = self.COLORES["border_dark"]
            gutter_bg = "#2A2A3C"
            gutter_fg = "#A6ADC8"
            self.btn_tema.config(text="☀️ Modo Claro", bg="#313244", fg="#CDD6F4")
        else:
            bg_gen = self.COLORES["light_bg"]
            fg_gen = self.COLORES["light_fg"]
            borde_editor = self.COLORES["border_light"]
            gutter_bg = "#E0E0E0"
            gutter_fg = "#666666"
            self.btn_tema.config(text="🌙 Modo Oscuro", bg="#E0E0E0", fg="#1E1E2E")

        self.root.config(bg=bg_gen)
        self.main_container.config(bg=bg_gen)
        self.frame_header.config(bg=bg_gen)
        self.lbl_titulo.config(bg=bg_gen, fg=fg_gen)
        self.frame_cuerpo.config(bg=bg_gen)
        self.frame_editor_container.config(bg=bg_gen)
        self.frame_res_container.config(bg=bg_gen)
        self.frame_botones.config(bg=bg_gen)
        self.frame_btn_left.config(bg=bg_gen)
        self.frame_btn_right.config(bg=bg_gen)
        self.lbl_fase_titulo.config(bg=bg_gen, fg=fg_gen)
        self.lbl_errores_titulo.config(bg=bg_gen, fg=fg_gen)

        self.frame_borde_editor.config(bg=borde_editor)
        self.editor_ide.linenumbers.config(bg=gutter_bg, fg=gutter_fg)

        for widget in (self.frame_editor_container, self.frame_res_container):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.config(bg=bg_gen, fg=fg_gen)

    def _cambiar_modo_analisis(self, modo: str):
        self.modo_analisis = modo
        self._actualizar_estilo_botones_modo()
        self._renderizar_resultados()

    def _actualizar_estilo_botones_modo(self):
        for clave, btn in self.btns_modo.items():
            if clave == self.modo_analisis:
                btn.config(bg="#313244" if self.dark_mode else "#1E1E2E", fg="#FFFFFF")
            else:
                btn.config(bg="#45475A" if self.dark_mode else "#E0E0E0", fg="#CDD6F4" if self.dark_mode else "#333333")

    # -----------------------------------------------------------------------
    # Acciones de los Botones Principales
    # -----------------------------------------------------------------------
    def _borrar_editor(self):
        self.editor_ide.text.delete("1.0", tk.END)
        self.editor_ide.resaltar_lineas_error(set())
        self.editor_ide.update_line_numbers()

        self.last_lex_tokens = []
        self.last_lex_errors = []
        self.last_ast = None
        self.last_syn_errors = []
        self.last_sem_errors = []
        self.last_lines_code = []

        self._set_panel(self.txt_fase, "", "neutral")
        self._set_panel(self.txt_errores, "", "neutral")

    def _cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo de código o texto",
            filetypes=[("Todos los archivos", "*.*"), ("Archivos Lua / Texto", "*.lua *.txt *.py")],
        )
        if ruta:
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                self.editor_ide.text.delete("1.0", tk.END)
                self.editor_ide.text.insert("1.0", contenido)
                self.editor_ide.update_line_numbers()
                self.editor_ide.resaltar_lineas_error(set())
            except Exception as e:
                messagebox.showerror("Error de lectura", f"No se pudo cargar el archivo:\n{e}")

    # -----------------------------------------------------------------------
    # Evaluación Secuencial del Código
    # -----------------------------------------------------------------------
    def _evaluar_codigo(self):
        codigo = self.editor_ide.text.get("1.0", tk.END).rstrip("\n")

        if not codigo.strip():
            return

        self.last_lines_code = codigo.split("\n")
        lineas_con_error = set()

        # --- 1. LÉXICO ---
        lexer.lexer.lineno = 1
        lexer.lexer.errores = []
        lexer.lexer.input(codigo)

        self.last_lex_tokens = []
        while True:
            tok = lexer.lexer.token()
            if not tok:
                break
            self.last_lex_tokens.append(tok)

        self.last_lex_errors = list(lexer.lexer.errores)

        for err_msg in self.last_lex_errors:
            match = re.search(r"línea\s+(\d+)", err_msg, re.IGNORECASE)
            if match:
                lineas_con_error.add(int(match.group(1)))

        # --- 2. SINTÁCTICO ---
        self.last_ast = None
        self.last_syn_errors = []

        try:
            self.last_ast = sintactico.parse(codigo)
        except sintactico.ParseError as error:
            self.last_syn_errors = str(error).splitlines()
            for err_msg in self.last_syn_errors:
                match = re.search(r"línea\s+(\d+)", err_msg, re.IGNORECASE)
                if match:
                    lineas_con_error.add(int(match.group(1)))
        except Exception as ex:
            self.last_syn_errors = [f"Error sintáctico fatal: {ex}"]

        # --- 3. SEMÁNTICO ---
        self.last_sem_errors = []
        if self.last_ast is not None:
            analizador_sem = AnalizadorSemantico()
            self.last_sem_errors = analizador_sem.analizar(self.last_ast)
            for err in self.last_sem_errors:
                lineas_con_error.add(err.linea)

        self.editor_ide.resaltar_lineas_error(lineas_con_error)
        self._renderizar_resultados()

    # -----------------------------------------------------------------------
    # Renderizado Dinámico de Resultados con Mayor Espaciado
    # -----------------------------------------------------------------------
    def _renderizar_resultados(self):
        if not self.last_lines_code:
            return

        if self.modo_analisis == "completo":
            self._render_analisis_completo()
        elif self.modo_analisis == "lexico":
            self._render_modo_lexico()
        elif self.modo_analisis == "sintactico":
            self._render_modo_sintactico()
        elif self.modo_analisis == "semantico":
            self._render_modo_semantico()

    def _render_analisis_completo(self):
        self.lbl_fase_titulo.config(text="Resultado por Fase:")
        self.lbl_errores_titulo.config(text="Errores Encontrados:")

        txt_fases = "RESUMEN DE EVALUACIÓN POR ETAPA:\n\n"

        if self.last_lex_errors:
            txt_fases += f"1. Análisis Léxico:     ❌ [{len(self.last_lex_errors)} error(es)]\n\n"
        else:
            txt_fases += f"1. Análisis Léxico:     ✔ Correcto ({len(self.last_lex_tokens)} tokens)\n\n"

        if self.last_syn_errors:
            txt_fases += f"2. Análisis Sintáctico: ❌ [{len(self.last_syn_errors)} error(es)]\n\n"
        else:
            count_ast = len(self.last_ast) if self.last_ast else 0
            txt_fases += f"2. Análisis Sintáctico: ✔ Correcto ({count_ast} nodos AST)\n\n"

        if self.last_syn_errors:
            txt_fases += "3. Análisis Semántico:  ⚠️ Omitido (Hay errores sintácticos previos)\n"
        elif self.last_sem_errors:
            txt_fases += f"3. Análisis Semántico:  ❌ [{len(self.last_sem_errors)} error(es)]\n"
        else:
            txt_fases += "3. Análisis Semántico:  ✔ Correcto (Sin infracciones)\n"

        self._set_panel(self.txt_fase, txt_fases, "neutral")

        total_errores = len(self.last_lex_errors) + len(self.last_syn_errors) + len(self.last_sem_errors)

        if total_errores == 0:
            txt_err = "✔ EL CÓDIGO LUA ES TOTALMENTE VÁLIDO\n\nNo se encontraron errores léxicos, sintácticos ni semánticos."
            self._set_panel(self.txt_errores, txt_err, "exito")
        else:
            txt_err = f"❌ SE ENCONTRARON {total_errores} ERROR(ES) EN TOTAL:\n"
            txt_err += "═" * 45 + "\n\n"

            for err in self.last_lex_errors:
                txt_err += f"► [LÉXICO]\n  {err}\n\n"

            for err in self.last_syn_errors:
                txt_err += f"► [SINTÁCTICO]\n  {err}\n\n"

            for err in self.last_sem_errors:
                frag = self._obtener_fragmento(err.linea)
                txt_err += (
                    f"► [SEMÁNTICO - Línea {err.linea}]\n"
                    f"  Regla: [{err.regla}]\n"
                    f"  Detalle: {err.mensaje}\n"
                    f"  Fragmento: \"{frag}\"\n\n"
                )

            self._set_panel(self.txt_errores, txt_err, "error")

    def _render_modo_lexico(self):
        self.lbl_fase_titulo.config(text="Tokens Reconocidos (Léxico):")
        self.lbl_errores_titulo.config(text="Errores Léxicos:")

        txt_toks = f"Total Tokens: {len(self.last_lex_tokens)}\n\n"
        txt_toks += f"{'LÍNEA':<8} {'TIPO':<18} {'VALOR'}\n"
        txt_toks += "─" * 45 + "\n"
        for t in self.last_lex_tokens:
            txt_toks += f"{t.lineno:<8} {t.type:<18} {repr(t.value)}\n"

        self._set_panel(self.txt_fase, txt_toks, "neutral")

        if self.last_lex_errors:
            txt_err = "❌ ERRORES LÉXICOS DETECTADOS:\n\n"
            txt_err += "\n\n".join(f"► {e}" for e in self.last_lex_errors)
            self._set_panel(self.txt_errores, txt_err, "error")
        else:
            self._set_panel(self.txt_errores, "✔ Sin errores léxicos. Todos los caracteres fueron reconocidos correctamente.", "exito")

    def _render_modo_sintactico(self):
        self.lbl_fase_titulo.config(text="Estructura Sintáctica (AST):")
        self.lbl_errores_titulo.config(text="Errores Sintácticos:")

        if self.last_ast is not None:
            txt_ast = f"Nodos reconocidos: {len(self.last_ast)}\n\n"
            for i, stmt in enumerate(self.last_ast, 1):
                txt_ast += f"[{i}] {stmt}\n\n"
            self._set_panel(self.txt_fase, txt_ast, "neutral")
        else:
            self._set_panel(self.txt_fase, "No se generó el AST debido a errores sintácticos en la gramática.", "neutral")

        if self.last_syn_errors:
            txt_err = "❌ ERRORES SINTÁCTICOS DETECTADOS:\n\n"
            txt_err += "\n\n".join(f"► {e}" for e in self.last_syn_errors)
            self._set_panel(self.txt_errores, txt_err, "error")
        else:
            self._set_panel(self.txt_errores, "✔ Sin errores sintácticos. La estructura gramatical del programa es válida.", "exito")

    def _render_modo_semantico(self):
        self.lbl_fase_titulo.config(text="Análisis Semántico:")
        self.lbl_errores_titulo.config(text="Errores Semánticos:")

        txt_sem = "REGLAS EVALUADAS:\n\n"
        txt_sem += "• ID-DECL, ID-CONST (Julio)\n\n"
        txt_sem += "• OP-ARIT, OP-CONCAT (Valeria)\n\n"
        txt_sem += "• CTX-RETURN, CTX-BREAK (Juan Andrés)\n"
        self._set_panel(self.txt_fase, txt_sem, "neutral")

        if self.last_syn_errors:
            self._set_panel(self.txt_errores, "⚠️ Análisis semántico omitido debido a errores sintácticos previos.", "neutral")
        elif self.last_sem_errors:
            txt_err = "❌ ERRORES SEMÁNTICOS DETECTADOS:\n\n"
            for err in self.last_sem_errors:
                frag = self._obtener_fragmento(err.linea)
                txt_err += (
                    f"► [Línea {err.linea}] Regla [{err.regla}]\n"
                    f"  Mensaje: {err.mensaje}\n"
                    f"  Fragmento erróneo: \"{frag}\"\n\n"
                )
            self._set_panel(self.txt_errores, txt_err, "error")
        else:
            self._set_panel(self.txt_errores, "✔ Sin errores semánticos. El código cumple todas las reglas de ámbito, tipos y contexto.", "exito")

    def _obtener_fragmento(self, num_linea: int) -> str:
        if 1 <= num_linea <= len(self.last_lines_code):
            return self.last_lines_code[num_linea - 1].strip()
        return "Código inaccesible"

    def _set_panel(self, widget: tk.Text, texto: str, estado: str = "neutral"):
        widget.config(state=tk.NORMAL)
        widget.delete("1.0", tk.END)
        widget.insert("1.0", texto)

        if estado == "error":
            bg = self.COLORES["res_error_bg"]
            fg = self.COLORES["res_error_fg"]
        elif estado == "exito":
            bg = self.COLORES["res_exito_bg"]
            fg = self.COLORES["res_exito_fg"]
        else:
            bg = self.COLORES["res_neutral_bg"]
            fg = self.COLORES["res_neutral_fg"]

        widget.config(bg=bg, fg=fg, state=tk.DISABLED)


# ---------------------------------------------------------------------------
# Punto de Entrada
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app_root = tk.Tk()
    app = AnalizadorGUI(app_root)
    app_root.mainloop()