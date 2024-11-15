import numpy as np
import pandas as pd
from graphviz import Digraph


class Markov:
    def __init__(self, transitions, node_names=None, rewards=None, probs=None, values=None, ):
        # transitions의 타입에 따라 클래스 변수 초기화
        if isinstance(transitions, pd.DataFrame):
            self._transitions = transitions
            self._node_names = list(
                self._transitions.columns if (node_names is None) else node_names)

        elif isinstance(transitions, dict):
            self._transitions = self._dict_to_dataframe(transitions)
            self._node_names = list(
                self._transitions.columns if (node_names is None) else node_names)

        else:
            if isinstance(transitions, np.ndarray):
                if node_names is None:
                    self._node_names = [
                        f'Node_{i}' for i in range(transitions.shape[0])]
                else:
                    self._node_names = list(node_names)
                self._transitions = pd.DataFrame(
                    transitions, index=self._node_names, columns=self._node_names)
            elif isinstance(transitions, list):
                if node_names is None:
                    self._node_names = [
                        f'Node_{i}' for i in range(len(transitions[0]))]
                else:
                    self._node_names = list(node_names)
                self._transitions = pd.DataFrame(
                    transitions, index=self._node_names, columns=self._node_names)

            else:
                raise ValueError(
                    "Transitions must be a Pandas DataFrame, NumPy ndarray, list, or dict.")

        if rewards is not None:
            self._rewards = self._validate_and_convert_1d(rewards, 'rewards')
        if probs is not None:
            self._probs = self._validate_and_convert_1d(probs, 'probs')
        if values is not None:
            self._values = self._validate_and_convert_1d(values, 'values')

    @property
    def transitions(self):
        return self._transitions

    @property
    def node_names(self):
        return self._node_names

    @property
    def rewards(self):
        return self._is_variable_defined('_rewards')

    @property
    def probs(self):
        return self._is_variable_defined('_probs')

    @property
    def values(self):
        return self._is_variable_defined('_values')

    def transitions_as_array(self):
        return self._transitions.values

    def save_to_csv(self):
        pass

    def _dict_to_dataframe(self, _dict):
        df = pd.DataFrame(0, index=_dict.keys(), columns=_dict.keys())
        for from_state, destinations in _dict.items():
            for to_state, probability in destinations.items():
                df.loc[from_state, to_state] = probability

        return df

    def _dict_to_series(self, _dict):
        return pd.Series(_dict)

    def _validate_and_convert_1d(self, data, data_name):
        if isinstance(data, pd.Series):
            assert all((self._node_names == data.index)
                       ), f"The index of '{data_name}' does not match the node_names."

        elif isinstance(data, dict):
            data = self._dict_to_series(data)
            assert all((self._node_names == data.index)
                       ), f"The index of '{data_name}' does not match the node_names."

        elif isinstance(data, (np.ndarray, list)):
            data = pd.Series(data, index=self._node_names)
        else:
            raise ValueError(
                f"'{data_name}' must be a Pandas Series, NumPy ndarray, list, or dict.")

        return data[self._node_names]

    def _is_variable_defined(self, var_name):
        return hasattr(self, var_name, None)


class PlotMarkov:
    def __init__(self, markov):
        self.markov = markov
        self.transitions = self._dataframe_to_dict(markov.transitions)
        self._rewards = self._series_to_dict(
            markov.reward) if markov.reward is not None else {}
        self._probs = self._series_to_dict(
            markov.probs) if markov.probs is not None else {}
        self._values = self._series_to_dict(
            markov.values) if markov.values is not None else {}

    def _draw_graph(self, show_rewards=False, show_probabilities=False, show_values=False):
        graph = Digraph()
        graph.attr(rankdir='LR')
        graph.attr('node', shape='circle',
                   style='filled', fillcolor='lightblue')

        # Add nodes
        for state in self.transitions.keys():
            label = f'<B>{state}</B>'

            if show_rewards:
                r = self._rewards.get(state, 0)
                label += f'<br/><FONT COLOR="Black" POINT-SIZE="10">r = {r:.2f}</FONT>'
            if show_probabilities:
                p = self._probs.get(state, 0)
                label += f'<br/><FONT COLOR="Red" POINT-SIZE="10">p = {p:1.2f}</FONT>'
            if show_values:
                v = self._values.get(state, 0)
                label += f'<br/><FONT COLOR="Green" POINT-SIZE="10">v = {v:.2f}</FONT>'

            graph.node(state, label=f'<{label}>',
                       width='0.8', height='0.8', fixedsize='true')

        # Add edges with probabilities
        for from_state, destinations in self.transitions.items():
            for to_state, probability in destinations.items():
                graph.edge(from_state, to_state,
                           label=f' {probability:.2f} ')
        return graph

    def draw_graph_with_rewards(self):
        return self._draw_graph(show_rewards=True)

    def draw_graph_with_probs(self):
        return self._draw_graph(show_probabilities=True)

    def draw_graph_with_values(self):
        return self._draw_graph(show_values=True)

    def draw_graph_with_rewards_and_values(self):
        return self._draw_graph(show_rewards=True, show_values=True)

    def _dataframe_to_dict(self, frame):
        transitions = frame.T.to_dict()
        transitions = {
            from_state: {
                to_state: probability
                for to_state, probability in destinations.items() if probability != 0
            }
            for from_state, destinations in transitions.items()
        }
        return transitions

    def _series_to_dict(self, series):
        return series.to_dict()
