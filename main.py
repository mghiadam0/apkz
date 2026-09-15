import os
import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

Window.clearcolor = get_color_from_hex('#1a472a')

DB_PATH = os.path.join(App.get_running_app().user_data_dir if App.get_running_app() else '.', 'notes.db')

class NotesApp(App):
    def build(self):
        self.title = 'Quick Notes'
        self.db_path = os.path.join(self.user_data_dir, 'notes.db')
        self.init_db()
        
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # العنوان
        title = Label(
            text='📝 ملاحظاتي',
            size_hint_y=None,
            height=50,
            font_size='24sp',
            color=get_color_from_hex('#d4af37'),
            bold=True
        )
        root.add_widget(title)
        
        # منطقة عرض الملاحظات
        scroll = ScrollView(size_hint=(1, 0.6))
        self.notes_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None,
            padding=5
        )
        self.notes_layout.bind(minimum_height=self.notes_layout.setter('height'))
        scroll.add_widget(self.notes_layout)
        root.add_widget(scroll)
        
        # حقل الإدخال
        self.input_field = TextInput(
            hint_text='اكتب ملاحظتك هنا...',
            size_hint_y=None,
            height=100,
            multiline=True,
            background_color=get_color_from_hex('#f5e6c8'),
            foreground_color=get_color_from_hex('#1a472a'),
            font_size='16sp'
        )
        root.add_widget(self.input_field)
        
        # أزرار
        btn_layout = BoxLayout(size_hint_y=None, height=60, spacing=10)
        
        save_btn = Button(
            text='💾 حفظ',
            background_color=get_color_from_hex('#2d6a4f'),
            font_size='18sp'
        )
        save_btn.bind(on_press=self.save_note)
        btn_layout.add_widget(save_btn)
        
        clear_btn = Button(
            text='🗑️ مسح',
            background_color=get_color_from_hex('#8b0000'),
            font_size='18sp'
        )
        clear_btn.bind(on_press=self.clear_input)
        btn_layout.add_widget(clear_btn)
        
        root.add_widget(btn_layout)
        
        self.load_notes()
        return root
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS notes
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         content TEXT NOT NULL,
                         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()
    
    def save_note(self, instance):
        text = self.input_field.text.strip()
        if text:
            conn = sqlite3.connect(self.db_path)
            conn.execute('INSERT INTO notes (content) VALUES (?)', (text,))
            conn.commit()
            conn.close()
            self.input_field.text = ''
            self.load_notes()
    
    def clear_input(self, instance):
        self.input_field.text = ''
    
    def load_notes(self):
        self.notes_layout.clear_widgets()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute('SELECT id, content FROM notes ORDER BY id DESC')
        notes = cursor.fetchall()
        conn.close()
        
        if not notes:
            empty = Label(
                text='لا توجد ملاحظات بعد.\nاكتب ملاحظتك الأولى!',
                size_hint_y=None,
                height=80,
                color=get_color_from_hex('#f5e6c8'),
                font_size='16sp'
            )
            self.notes_layout.add_widget(empty)
            return
        
        for note_id, content in notes:
            note_box = BoxLayout(size_hint_y=None, height=60, spacing=5)
            
            lbl = Label(
                text=content,
                color=get_color_from_hex('#f5e6c8'),
                font_size='14sp',
                halign='right',
                valign='middle'
            )
            lbl.bind(size=lbl.setter('text_size'))
            note_box.add_widget(lbl)
            
            del_btn = Button(
                text='❌',
                size_hint_x=None,
                width=50,
                background_color=get_color_from_hex('#8b0000')
            )
            del_btn.bind(on_press=lambda x, nid=note_id: self.delete_note(nid))
            note_box.add_widget(del_btn)
            
            self.notes_layout.add_widget(note_box)
    
    def delete_note(self, note_id):
        conn = sqlite3.connect(self.db_path)
        conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        conn.commit()
        conn.close()
        self.load_notes()

if __name__ == '__main__':
    NotesApp().run()
