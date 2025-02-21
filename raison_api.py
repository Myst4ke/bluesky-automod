import requests

class API:

    def __init__(self, proj_id, api_key, version):
        self._proj_id = proj_id
        self._api_key = api_key
        self._version = version
        try:
            metadata = self.get_metadata()
            if metadata:
                self._elements = {element['label']:element['id'] for element in metadata['elements']}
                self._options = {option['label']:option['id'] for option in metadata['options']}
        except RuntimeError:
            raise RuntimeError


    def api_run(self, elements):
        if all(e in self._elements for e in elements):
            body_elements = []
            for element in elements:
                body_elements.append({"label":element, "id":self._elements[element]})
            data = {
                "elements": body_elements,
                "options": [
                    {
                        "label": opt,
                        "id": self._options[opt]
                    }
                    for opt in self._options if opt == "block post"
                ]
            }

            url, headers = self.get_url(), self.get_headers()
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    options = response.json()
                    print(options)
                    res = {option["option"]["label"]:option["isSolution"] for option in options}
                    return res
                elif response.status_code == 400:
                    print("Erreur 400 : Requête invalide.")
                    raise RuntimeError
                else:
                    print(f"Erreur {response.status_code} : {response.text}")
                    raise RuntimeError
            except Exception as e:
                print(f"Impossible d'exécuter cette requête : {e}")
        else:
            raise ValueError(f"Certains éléments ne font pas partie du projet, vérifier s'il n'y a pas de typo.\nListe de éléments donnés : {elements}\nListe des éléments dans le projet : {self._elements}")


    def get_url(self):
        return f"https://api.ai-raison.com/executions/{self._proj_id}/{self._version}"

    def get_headers(self):
        headers = {
            "x-api-key": self._api_key
        }
        return headers


    def get_metadata(self):

        url = self.get_url()
        headers = self.get_headers()

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                metadata = response.json()
                return metadata
            elif response.status_code == 400:
                print("Erreur 400 : Requête invalide.")
                raise RuntimeError
            else:
                print(f"Erreur {response.status_code} : {response.text}")
                raise RuntimeError
        except Exception as e:
            print(f"Impossible de récupérer les matadatas du projet : {e}")


if __name__ == "__main__":
    a = API("PRJ17525", "gHWO8Hpd2LPSLkCyseUZ836NS0LtHGEFhyxIrKj0", "latest")

    elements = ["is viral", "is in followed feed", "has used banword", "is 5% of followings blocked accounts"]

    res = a.api_run(elements)
    print(res)
