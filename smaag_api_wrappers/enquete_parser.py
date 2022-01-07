import os
import pandas as pd


class EnqueteParser:

    TYPOLOGY_MAPPING = {
        'MD':'Montée Descente',
        'MLIG': 'Montée par ligne de correspondance',
        'DLIG': 'Descente par ligne de correspondance',
        'MMOD': 'Montée par mode de correspondance',
        'DMOD': 'Descente par mode de correspondance'
    }

    GOAL_MAPPING = {
        'MOTIFOD1': 'Domicile --> Travail',
        'MOTIFOD2': 'Domicile --> Ecole|Collège|Lycée',
        'MOTIFOD3': 'Domicile --> Université|Fac',
        'MOTIFOD4': 'Domicile --> Achats|Courses',
        'MOTIFOD5': 'Domicile --> Loisirs|Visites',
        'MOTIFOD6': 'Domicile --> Démarches Administrative|Medecin',
        'MOTIFOD7': 'Domicile --> Autres Motifs',
        'MOTIFOD8': 'Autres Motifs'
    }

    WAYS = ['S1','S2']

    TIMELAPS_MAPPING = {
        'PpetitM':'02H00-06H45',
        'PPM':'06H45-08H45',
        'Pcm':'08H45-11H30',
        'PPMidi':'11H30-13H30',
        'Pcam':'13H30-15H30',
        'PPS':'15H30-18H30',
        'Pfj':'18H30-21H00',
        'Pnuit':'21H00-02H00'
    }

    def __init__(self, file_path):

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier enquête {file_path} n'existe pas")
        self.file_path = file_path
        self.line = os.path.basename(file_path).split('.')[0]

    def parse(self):
        df = pd.read_excel(self.file_path,sheet_name='SOMMAIRE', header=None, names=['sheet','sheet_desc'])
        sheets = df['sheet'].tolist()

        df_md = pd.DataFrame()
        df_mdlig = pd.DataFrame()
        df_mdmod = pd.DataFrame()

        for sheet in sheets:
            categories = sheet.split('-')
            typology = categories[0]
            part2 = categories[1] if len(categories)>=2 else None
            part3 = categories[2] if len(categories)==3 else None

            way = None
            goal = None
            timelaps = None

            if part2 in self.WAYS:
                way = part2

            if part2 in self.TIMELAPS_MAPPING.keys():
                timelaps = part2
            elif part2 in self.GOAL_MAPPING.keys():
                goal = part2

            if part3 in self.TIMELAPS_MAPPING.keys():
                timelaps = part3
            elif part3 in self.GOAL_MAPPING.keys():
                goal = part3

            if typology == 'MD':
                df = self._parse_md(sheet, way, timelaps, goal)
                df_md = df_md.append(df)
            elif typology in ('MLIG','DLIG'):
                df = self._parse_mdlig(sheet, way, timelaps, goal, typology)
                df_mdlig = df_mdlig.append(df)
            elif typology in ('MMOD', 'DMOD'):
                df = self._parse_mdmod(sheet, way, timelaps, goal, typology)
                df_mdmod = df_mdmod.append(df)

        return df_md,df_mdlig,df_mdmod

    def _parse_md(self, sheetname, way, timelaps, goal):
        print(f"{sheetname}")
        df = pd.read_excel(self.file_path, sheet_name=sheetname, header=0, skiprows=lambda x: x in [0,1,2,3,4,5])
        cols_to_rem = ['Total'] if way is None else ['Montées','Descentes','Charge']
        df = df.drop(columns=cols_to_rem)
        df = df.rename(columns={"Matrice montée / descente": "up_cluster_name"})
        df = df[~df.up_cluster_name.str.contains('Total')]
        cols = list(set(df.columns) - {'up_cluster_name'})

        # unpivot cols
        df = df.melt(id_vars=['up_cluster_name'], value_vars=cols, var_name='down_cluster_name', value_name='passengers_count')

        df:pd.DataFrame = df[df.up_cluster_name!=df.down_cluster_name]
        df['passengers_count'] = df['passengers_count'].fillna(0)
        df['line_direction']= 'ALL' if way is None else way
        df['timelaps'] = 'ALL' if timelaps is None else self.TIMELAPS_MAPPING.get(timelaps)
        df['goal'] = 'ALL' if goal is None else self.GOAL_MAPPING.get(goal)
        df['line'] = self.line
        return df

    def _parse_mdlig(self, sheetname, way, timelaps, goal, typology):
        print(f"{sheetname}")
        df = pd.read_excel(self.file_path, sheet_name=sheetname, header=0, skiprows=lambda x: x in [0,1,2,3])
        cols_to_rem = ['Total général']
        df = df.drop(columns=cols_to_rem)
        cols_to_rename = {"Montée par ligne amont": "cluster_name", "Montée par ligne aval": "cluster_name"} if typology == 'MLIG' \
            else {"Descente par ligne amont": "cluster_name", "Descente par ligne aval": "cluster_name"}
        df = df.rename(columns=cols_to_rename)
        df = df[~df.cluster_name.str.contains('Total')]
        cols = list(set(df.columns) - {'cluster_name'})

        # unpivot cols
        df = df.melt(id_vars=['cluster_name'], value_vars=cols, var_name='target_line', value_name='passengers_count')

        df['passengers_count'] = df['passengers_count'].fillna(0)
        df['up_down']='up' if typology=='MLIG' else 'down'
        df['line_direction']= 'ALL' if way is None else way
        df['timelaps'] = 'ALL' if timelaps is None else self.TIMELAPS_MAPPING.get(timelaps)
        df['goal'] = 'ALL' if goal is None else self.GOAL_MAPPING.get(goal)
        df['line'] = self.line
        return df

    def _parse_mdmod(self, sheetname, way, timelaps, goal, typology):
        print(f"{sheetname}")
        df = pd.read_excel(self.file_path, sheet_name=sheetname, header=0, skiprows=lambda x: x in [0,1,2,3])
        df = df.drop(columns='Total général')
        df = df.rename(columns={"Montée par mode amont": "cluster_name", "Descente par mode aval": "cluster_name"})
        df = df[~df.cluster_name.str.contains('Total')]
        cols = list(set(df.columns) - {'cluster_name'})

        # unpivot cols
        df = df.melt(id_vars=['cluster_name'], value_vars=cols, var_name='target_mode', value_name='passengers_count')

        df['passengers_count'] = df['passengers_count'].fillna(0)
        df['up_down']='up' if typology=='MLIG' else 'down'
        df['line_direction']= 'ALL' if way is None else way
        df['timelaps'] = 'ALL' if timelaps is None else self.TIMELAPS_MAPPING.get(timelaps)
        df['goal'] = 'ALL' if goal is None else self.GOAL_MAPPING.get(goal)
        df['line'] = self.line
        return df