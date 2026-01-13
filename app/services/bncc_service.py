# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
import json
import os

class BNCCService:
    _data = None

    @classmethod
    def load_data(cls):
        if cls._data is None:
            cls._data = []
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            # Load Infantil
            try:
                path = os.path.join(base_path, 'data', 'bncc_infantil.json')
                with open(path, 'r', encoding='utf-8') as f:
                    cls._data.extend(json.load(f))
            except Exception as e:
                print(f"Error loading Infantil BNCC: {e}")

            # Load Fundamental
            try:
                path = os.path.join(base_path, 'data', 'bncc_fundamental.json')
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cls._process_fundamental(data)
            except Exception as e:
                print(f"Error loading Fundamental BNCC: {e}")

            # Load Medio
            try:
                path = os.path.join(base_path, 'data', 'bncc_medio.json')
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cls._process_medio(data)
            except Exception as e:
                print(f"Error loading Medio BNCC: {e}")

        return cls._data

    @classmethod
    def _process_fundamental(cls, data):
        """Normalize Fundamental data into the standard list structure."""
        # Fundamental JSON structure: { discipline_key: { "ano": [ { "nome_ano": [...], "unidades_tematicas": [...] } ] } }
        for discipline_key, content in data.items():
            discipline_name = discipline_key.replace('_', ' ').title()
            for ano_group in content.get('ano', []):
                # Anos can be a list: ["1º", "2º"]
                anos = ", ".join(ano_group.get('nome_ano', []))

                for unidade in ano_group.get('unidades_tematicas', []):
                    title = f"{discipline_name} - {unidade.get('nome_unidade', '')} ({anos})"

                    items = []
                    for objeto in unidade.get('objeto_conhecimento', []):
                        obj_name = objeto.get('nome_objeto', '')
                        for hab in objeto.get('habilidades', []):
                            # Habilidade name often contains the code: "(EF01LP01) Description..."
                            raw_text = hab.get('nome_habilidade', '')
                            code = ""
                            desc = raw_text

                            # Extract code if present at start
                            if raw_text.startswith('('):
                                end_idx = raw_text.find(')')
                                if end_idx != -1:
                                    code = raw_text[1:end_idx]
                                    desc = raw_text[end_idx+1:].strip()

                            items.append({
                                "code": code,
                                "description": f"{obj_name}: {desc}",
                                "range": anos
                            })

                    if items:
                        cls._data.append({
                            "title": title,
                            "itens": items
                        })

    @classmethod
    def _process_medio(cls, data):
        """Normalize Medio data into the standard list structure."""
        # Medio JSON structure: { discipline_key: { "ano": [ { "nome_ano": [...], "codigo_habilidade": [...] } ] } }
        for discipline_key, content in data.items():
            discipline_name = content.get('nome_disciplina', discipline_key.replace('_', ' ').title())

            for ano_group in content.get('ano', []):
                anos = ", ".join(ano_group.get('nome_ano', []))

                items = []
                # Medio uses "codigo_habilidade" list directly
                for hab in ano_group.get('codigo_habilidade', []):
                    code = hab.get('nome_codigo', '')
                    desc = hab.get('nome_habilidade', '')

                    items.append({
                        "code": code,
                        "description": desc,
                        "range": anos
                    })

                if items:
                    cls._data.append({
                        "title": f"{discipline_name} ({anos})",
                        "itens": items
                    })

    @classmethod
    def search_skills(cls, query: str = "") -> list[dict]:
        """
        Searches for BNCC skills.
        Returns a list of dicts: {'code': str, 'description': str, 'title': str}
        """
        data = cls.load_data()
        results = []
        query = query.lower().strip()

        for group in data:
            group_title = group.get('title', '')
            for item in group.get('itens', []):
                code = item.get('code', '')
                description = item.get('description', '')

                # Search in code, description, and group title (for context)
                if not query or (query in code.lower() or query in description.lower() or query in group_title.lower()):
                    results.append({
                        "code": code,
                        "description": description,
                        "title": group_title
                    })
        return results

    @classmethod
    def get_skill_by_code(cls, code: str) -> dict | None:
        data = cls.load_data()
        code_clean = code.strip().upper()
        for group in data:
            for item in group.get('itens', []):
                if item.get('code', '').strip().upper() == code_clean:
                    return {
                        "code": item['code'],
                        "description": item['description'],
                        "title": group.get('title', '')
                    }
        return None
