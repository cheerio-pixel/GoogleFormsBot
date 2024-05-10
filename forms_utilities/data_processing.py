"""Module in charge of creating charts and Frequency tables.
"""
from functools import reduce
from typing import Any, Self
from collections import Counter
import pandas as pd
from pandas.plotting import table
import matplotlib.pyplot as plt
import dataframe_image as dfi
import textwrap
import forms_api

pd.set_option("colheader_justify", "center")


class SuperSantosMachine:
    def __init__(
        self,
        title: str,
        frequency_data: dict[str, int],
        var_col_name="x",
        freq_col_name="fi",
        accum_freq_col_name="Fi",
        rel_freq_col_name="fr",
        rel_freq_perc_col_name="%",
        accum_rel_freq_col_name="Fr",
        footer_label="Total",
    ):
        self.frequency_data = frequency_data
        self._frequency_table: pd.DataFrame | pd.Series | None = None

        # The title of this frequency table
        self.title = title

        self.var_col_name = var_col_name
        self.freq_col_name = freq_col_name
        self.accum_freq_col_name = accum_freq_col_name
        self.rel_freq_col_name = rel_freq_col_name
        self.rel_freq_perc_col_name = rel_freq_perc_col_name
        self.accum_rel_freq_col_name = accum_rel_freq_col_name

        self.footer_label = footer_label

    @property
    def frequency_table(self) -> pd.DataFrame | pd.Series:
        if self._frequency_table is None:
            self._frequency_table = self.compute_frequency_table()
        return self._frequency_table

    def compute_frequency_table(self):
        """Creates a pandas DataFrame from frequency data.

        frequency_data is dictionary of variables with their respectives
        absolute frequency.

        NOTE: This frequency table is highly opininated to please a
        man called Santos. I will not give surname because those who
        know, know
        """
        df = pd.DataFrame(
            {
                self.var_col_name: self.frequency_data.keys(),
                self.freq_col_name: self.frequency_data.values(),
            }
        )
        number_of_responses = df[self.freq_col_name].sum()
        df[self.rel_freq_col_name] = (
            df[self.freq_col_name] / number_of_responses
        )
        # Round up by 4 places
        df[self.rel_freq_col_name] = df[self.rel_freq_col_name].round(4)

        df[self.rel_freq_perc_col_name] = df[self.rel_freq_col_name] * 100
        # Round up by 2 places
        df[self.rel_freq_perc_col_name] = df[
            self.rel_freq_perc_col_name
        ].round(2)

        df[self.accum_freq_col_name] = df[self.freq_col_name].cumsum()

        df[self.accum_freq_col_name] = df[self.accum_freq_col_name].astype(
            df[self.freq_col_name].dtypes
        )

        df[self.accum_rel_freq_col_name] = (
            df[self.accum_freq_col_name] / number_of_responses
        ) * 100

        # Round up by 2 places
        df[self.accum_rel_freq_col_name] = df[
            self.accum_rel_freq_col_name
        ].round(4)

        # Add column with the total of the previous
        df[self.footer_label] = False

        footer = pd.DataFrame(
            {
                self.var_col_name: [self.footer_label],
                self.freq_col_name: [number_of_responses],
                # accum_freq_col_name: np.NaN,
                self.rel_freq_col_name: [
                    df[self.rel_freq_col_name].sum().round(0)
                ],
                # accum_rel_freq_col_name: np.NaN,
                self.rel_freq_perc_col_name: [
                    df[self.rel_freq_perc_col_name].sum().round(0)
                ],
            }
        )
        df = (
            pd.concat(
                [df[df[self.footer_label] == False], footer], ignore_index=True
            )
            .drop(columns=[self.footer_label])
            .fillna(dict.fromkeys(self.var_col_name, self.footer_label))
        )

        # End of the adding the total of the previous

        return df

    @classmethod
    def from_forms_api(
        cls,
        api: forms_api.FormsAPI,
        **kwargs,
    ) -> list[Self]:
        responses: list[list[list[str]]] = [
            res.order_by_questions(api.form.questions) for res in api.responses
        ]
        res: list[Self] = []
        for column, question in zip(zip(*responses[::-1]), api.form.questions):
            column: list[list[str]]
            res.append(
                cls(
                    question.title,
                    get_frequency_data(question.options, flatten(column)),
                    **kwargs,
                )
            )
        return res

    @classmethod
    def from_lists(
        cls,
        questions: list[str],
        responses: list[list[list[str]]],
        question_options: list[list[str]],
        **kwargs,
    ) -> list[Self]:
        """This assumes that each column of responses is paired with it's question options and each question with each question"""
        res: list[Self] = []
        for column, options, question in zip(
            zip(*responses[::-1]), question_options, questions
        ):
            column: list[list[str]]
            res.append(
                cls(
                    question,
                    get_frequency_data(flatten(column), options),
                    **kwargs,
                )
            )
        return res


class Grapher:
    """Class that graciously creates a matplotlib of frequency table"""

    def __init__(self, frequency_table: SuperSantosMachine):
        self.frequency_table = frequency_table
        self.figsize = (8, 8)

    def graph_bar_plot(self):
        # Drop last row
        df = self.frequency_table.frequency_table[:-1]
        # Figure Size
        fig, ax = plt.subplots(figsize=self.figsize, dpi=300)

        # Horizontal Bar Plot
        bars = ax.bar(
            df[self.frequency_table.var_col_name].map(
                lambda x: "\n".join(textwrap.wrap(x, width=25))
            ),
            df[self.frequency_table.rel_freq_perc_col_name],
            # list(reversed(self.frequency_table.frequency_data.keys())),
            # list(reversed(self.frequency_table.frequency_data.values())),
        )

        # Remove axes splines
        for s in ["top", "bottom", "left", "right"]:
            ax.spines[s].set_visible(False)

        # Remove x, y Ticks
        # ax.xaxis.set_ticks_position("none")
        # ax.yaxis.set_ticks_position("none")

        # Add padding between axes and labels
        ax.xaxis.set_tick_params(pad=5)
        ax.yaxis.set_tick_params(pad=10)

        # Add x, y gridlines
        ax.grid(color="grey", linestyle="-.", linewidth=0.5, alpha=0.2)

        # Show top values
        ax.invert_yaxis

        # Add annotation to bars
        # for i in ax.patches:
        #     plt.text(
        #         i.get_width() + 0.6,
        #         i.get_y() + i.get_height() / 2,
        #         str(round((i.get_width()), 2)),
        #         fontsize=20,
        #         fontweight="bold",
        #         color="grey",
        #     )
        ax.bar_label(
            bars,
            padding=2,
            color="white",
            # fontsize=12,
            fontsize=16,
            label_type="edge",
            fmt="%g%%",
            fontweight="bold",
        )
        if (
            reduce(max, map(len, self.frequency_table.frequency_data.keys()))
            > 20
        ):
            plt.xticks(
                rotation=41
                ha="right",
                wrap=True,
            )

        # for label in ax.get_xticklabels():
        #     # label.set_fontsize(16)
        #     label.set_wrap(True)
        # Add Plot Title

        fig.suptitle(
            self.frequency_table.title,
            fontsize=16,
            wrap=True,
        )
        # ax.set_title(
        #     self.frequency_table.title,
        #     loc="left",
        #     wrap=True,
        # )
        return fig, ax

    def graph_horizontal_bar_plot(self):
        # Figure Size
        fig, ax = plt.subplots(figsize=self.figsize, dpi=300)

        # Horizontal Bar Plot
        bars = ax.barh(
            list(reversed(self.frequency_table.frequency_data.keys())),
            list(reversed(self.frequency_table.frequency_data.values())),
        )
        for label in ax.get_yticklabels():
            # label.set_fontsize(16)
            label.set_wrap(True)

        # Remove axes splines
        for s in ["top", "bottom", "left", "right"]:
            ax.spines[s].set_visible(False)

        # Remove x, y Ticks
        ax.xaxis.set_ticks_position("none")
        ax.yaxis.set_ticks_position("none")

        # Add padding between axes and labels
        ax.xaxis.set_tick_params(pad=5)
        ax.yaxis.set_tick_params(pad=10)

        # Add x, y gridlines
        ax.grid(color="grey", linestyle="-.", linewidth=0.5, alpha=0.2)

        # Show top values
        ax.invert_yaxis

        # Add annotation to bars
        # for i in ax.patches:
        #     plt.text(
        #         i.get_width() + 0.6,
        #         i.get_y() + i.get_height() / 2,
        #         str(round((i.get_width()), 2)),
        #         fontsize=20,
        #         fontweight="bold",
        #         color="grey",
        #     )
        ax.bar_label(
            bars,
            padding=2,
            color="white",
            # fontsize=12,
            fontsize=16,
            label_type="edge",
            fmt="%g",
            fontweight="bold",
        )
        # Add Plot Title

        fig.suptitle(
            self.frequency_table.title,
            fontsize=16,
            wrap=True,
        )
        # ax.set_title(
        #     self.frequency_table.title,
        #     loc="left",
        #     wrap=True,
        # )
        return fig, ax

    def graph_pie_plot(self):
        df = self.frequency_table.frequency_table[:-1]
        fig, ax = plt.subplots(figsize=self.figsize, dpi=300)
        patches, *_ = ax.pie(df[self.frequency_table.rel_freq_col_name])
        labels = [
            "{1:>6.2f} % - {0}".format(x, perc)
            for x, perc in zip(
                df[self.frequency_table.var_col_name],
                df[self.frequency_table.rel_freq_perc_col_name],
            )
        ]
        fig.suptitle(
            self.frequency_table.title,
            fontsize=16,
            wrap=True,
        )
        fig.legend(
            patches,
            labels,
            loc="center left",
            fontsize=16,
            bbox_to_anchor=(0.5, -0.1),
            # bbox_to_anchor=(1, 0.5),
            # bbox_to_anchor=(0.8, 0.5),
        )
        return fig, ax


# def main():
#     creds = service_account.Credentials.from_service_account_file(
#         SERVICE_KEY_FILE,
#     ).with_scopes(SCOPES)
#     # api = FormsAPI(creds)
#     api = FormsAPI(creds)
#     responses_list = api.get_responses(
#         api.get_answers(EDIT_FORM_ID),
#     )
#     schema = api.get_schema(EDIT_FORM_ID)
#     titles = api.get_titles(EDIT_FORM_ID)

#     # df = api.get_dataframe(EDIT_FORM_ID)

#     schema_options = [api.get_options(o) for o in schema.get("items")]

#     result = ""
#     for responses, title, possible_options, i in zip(
#         zip(*responses_list[::-1]),
#         titles,
#         schema_options,
#         range(len(schema_options)),
#     ):
#         frequency_data = get_frequency_data(
#             possible_options, flatten(responses)
#         )
#         # with plt.style.context(matplotx.styles.challenger_deep):
#         #     make_bar_plot(frequency_data, title)

#         df = get_frequency_table(frequency_data)
#         # print(df.to_string(index=False))

#         # # Drop last
#         # df.drop(df.tail(1).index)
#         # with plt.style.context(matplotx.styles.challenger_deep):
#         #     # make_bar_plot(frequency_data, title)
#         #     make_pie_plot(df[:-1])

#         # plt.show()

#         # # Create visual representation in html
#         # print(title)
#         # print(df.to_string(index=False))

#         result += export_dataframe_to_html_with_sytle(df)

#     print(result, file=open("freq_tables.html", "+w"))


class CssStyle(dict):
    def __init__(self, selector: str, props: str | list[str]):
        self["selector"] = selector
        self["props"] = props


def export_dataframe_to_html_with_sytle(df: pd.DataFrame | pd.Series) -> str:
    """Return table with my biased css style and other formatting"""

    # for row hover use <tr> instead of <td>
    cell_hover = CssStyle("td:hover", "background-color: #ffffb3")

    header_footer_props = "background-color: #ADD8E6; color: black;"

    footer = CssStyle("tr:last-child", header_footer_props)

    headers = CssStyle("th:not(.index_name)", header_footer_props)

    alternating_color = CssStyle(
        "tr:nth-child(even):not(:last-child)", "background-color: lightgray;"
    )

    border = CssStyle(
        "th, td", "border: 2px solid black; border-style: double;"
    )
    border_table = CssStyle(
        ".static table",
        "border-spacing: 0px; border-collapse: separate; border: 1px solid black;",
    )

    return (
        df.fillna("")
        .astype("str")
        .replace(r"\.0$", "", regex=True)
        .style.set_table_styles(
            [
                CssStyle(
                    "tr:last-child", "background-color: #e51a4c; color: white;"
                ),
                CssStyle(
                    "th:not(.index_name)",
                    "background-color: #e51a4c; color: white;",
                )
                # cell_hover,
                # footer,
                # headers,
                # alternating_color,
                # border,
                # border_table,
            ]
        )
        .hide(subset=None, level=None, names=False)
        .to_html()
    )


# def make_pie_plot(df):
#     pied = plt.pie(df["fr"])
#     labels = [
#         "{1:>6.2f} % - {0}".format(x, perc)
#         for x, perc in zip(df["x"], df["%"])
#     ]
#     plt.legend(pied[0], labels, bbox_to_anchor=(1.01, 1))


# def make_bar_plot(frequency_data, title):
#     # Figure Size
#     fig, ax = plt.subplots(figsize=(16, 9))

#     # Horizontal Bar Plot
#     ax.barh(list(frequency_data.keys()), list(frequency_data.values()))

#     # Remove axes splines
#     for s in ["top", "bottom", "left", "right"]:
#         ax.spines[s].set_visible(False)

#     # Remove x, y Ticks
#     ax.xaxis.set_ticks_position("none")
#     ax.yaxis.set_ticks_position("none")

#     # Add padding between axes and labels
#     ax.xaxis.set_tick_params(pad=5)
#     ax.yaxis.set_tick_params(pad=10)

#     # Add x, y gridlines
#     ax.grid(color="grey", linestyle="-.", linewidth=0.5, alpha=0.2)

#     # Show top values
#     ax.invert_yaxis()

#     # Add annotation to bars
#     for i in ax.patches:
#         plt.text(
#             i.get_width() + 0.2,
#             i.get_y() + 0.5,
#             str(round((i.get_width()), 2)),
#             fontsize=10,
#             fontweight="bold",
#             color="grey",
#         )

#     # Add Plot Title
#     ax.set_title(
#         title,
#         loc="left",
#     )


def get_frequency_data(
    possible_options: list[str], responses: list[str]
) -> dict[str, int]:
    """Returns Dictionary with possible options as keys and their frequency as values"""
    default_count_dict = dict(
        zip(possible_options, [0] * len(possible_options))
    )

    frecuency_data = merge(default_count_dict, Counter(responses))
    return frecuency_data


def merge(dict1, dict2):
    """Return the union of two dictionaries.
    If there is common data between the two, the second dictionary takes precedence
    """
    return {**dict1, **dict2}


def flatten(_list: list[list[Any]]) -> list[Any]:
    return [l for sublist in _list for l in sublist]


def make_table_png(df, name):
    ax = plt.subplot(frame_on=False)  # no visible frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis

    table(
        ax,
        df,
        # cellLoc="center",
    )

    # plt.show()
    # ax.margins(x=0, y=0)
    plt.savefig(
        f"images/{name}.png",
        dpi=300,
        bbox_inches="tight",
    )


def make_table_png_with_dfi(df, name):
    df_styled = df.style.set_table_styles(
        [
            dict(selector="th", props=[("text-align", "center")]),
        ]
    )

    dfi.export(df_styled, f"images/{name}.png", dpi=300)


if __name__ == "__main__":
    main()
