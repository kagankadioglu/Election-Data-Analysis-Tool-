from Tkinter import *
import tkFileDialog
from PIL import Image,ImageTk
from ttk import Combobox
import clusters

class Application(Frame):
    def __init__(self, parent):
        Frame.__init__(self,parent)
        self.initUI()
        self.state = "inactive"
        #state remembers last clicked cluster button so when user clicks the refine analysis button
        #program is going to perform analysis on districts or parties with the information it gets from state.
        self.data_manager = DataCenter()  #this is data center object to manage data processes.

    def initUI(self):
        self.pack(fill=BOTH)
        self.UI_frame = Frame(self)
        self.UI_frame.pack(side=TOP,fill=BOTH)
        self.header = Label(self.UI_frame,text="Election Data Analysis Tool v.1.0",background="red",font=('Arial','23','bold'),
                            foreground="white")
        self.header.pack(side=TOP,fill=BOTH,ipady=7)
        self.upload_data_button = Button(self.UI_frame,text="Load Election Data",height=2,width=20,command=self.upload_data)
        self.cluster_district_button = Button(self.UI_frame,text="Cluster Districts",height=2,width=20,command=self.cluster_district)
        self.cluster_parties_button = Button(self.UI_frame,text="Cluster Political Parties",height=2,width=20,command=self.cluster_parties)
        self.upload_data_button.pack(side=TOP,pady=10)
        self.cluster_district_button.pack(side=LEFT,padx=(255,10))
        self.cluster_parties_button.pack(side=LEFT)

        self.analysis_frame = Frame(self)
        self.canvas_frame = Frame(self.analysis_frame)
        self.canvas_frame.pack(side=TOP, fill=BOTH, padx=90, pady=10)
        self.canvas_horizontal_scroll = Scrollbar(self.canvas_frame, orient="horizontal")
        self.canvas_vertical_scroll = Scrollbar(self.canvas_frame, orient="vertical")
        self.canvas = Canvas(self.canvas_frame, background="white", height=250, width=700)
        self.canvas.grid(row=0, column=0)
        self.canvas_horizontal_scroll.grid(row=1, column=0, columnspan=2, sticky=W+E)
        self.canvas_vertical_scroll.grid(row=0, column=1, sticky=S+N)
        self.canvas.configure(xscrollcommand=self.canvas_horizontal_scroll.set,
                              yscrollcommand=self.canvas_vertical_scroll.set)
        self.canvas_horizontal_scroll.configure(command=self.canvas.xview)
        self.canvas_vertical_scroll.configure(command=self.canvas.yview)
        self.canvas.configure(scrollregion=(0, 0, 1200, 800))
        #scrollregion helps us to cover all of the dendogram with scrollbars.
        self.panel_frame = Frame(self.analysis_frame)
        self.panel_frame.pack(side=TOP, fill=BOTH)
        self.district_label = Label(self.panel_frame, text="Districts:")
        self.district_listbox = Listbox(self.panel_frame,selectmode="multiple")
        self.listbox_scroll = Scrollbar(self.panel_frame)
        self.district_listbox.configure(yscrollcommand=self.listbox_scroll.set)
        self.listbox_scroll.configure(command=self.district_listbox.yview)
        self.threshold_label = Label(self.panel_frame, text="Threshold:")
        threshold_list = ["%0","%1","%10","%20","%30","%40","%50"] #list for threshold combobox
        self.threshold_combobox = Combobox(self.panel_frame, width=7,state="readonly",values=threshold_list)
        self.threshold_combobox.current(0) #default threshold is %0
        self.refine_button = Button(self.panel_frame, text="Refine Analysis", height=2, width=20,command=self.refined_analysis)
        self.district_label.pack(side=LEFT, padx=(120, 5))
        self.district_listbox.pack(side=LEFT)
        self.listbox_scroll.pack(side=LEFT, fill=Y)
        self.threshold_label.pack(side=LEFT, padx=10)
        self.threshold_combobox.pack(side=LEFT)
        self.refine_button.pack(side=LEFT, padx=20)

    def upload_data(self):
        self.district_listbox.delete(0, END)
        txt_file = tkFileDialog.askopenfilename(title="Select file",filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        self.data_manager.txt_manager(txt_file) #txt reader function
        self.data_manager.create_matrix(district_list=self.data_manager.district_dictionary.keys(),threshold="%0")
        #program creates matrix with default values which is all districts and %0 threshold right after reading txt.
        for district in sorted(self.data_manager.district_dictionary.keys()):
            self.district_listbox.insert(END,district)
        #inserting districts to listbox

    def cluster_district(self):
        self.state = "district"
        #if user clickes cluster districts state changes to district.
        self.analysis_frame.pack(side=TOP, fill=BOTH)
        self.canvas.delete("all") #clearing canvas
        # https://stackoverflow.com/questions/15839491/how-to-clear-tkinter-canvas
        self.party_list, self.district_list, self.data = clusters.readfile("matrix.txt")
        new_data = clusters.rotatematrix(self.data)
        #we need to rotated matrix to cluster districts.
        clust = clusters.hcluster(new_data,distance=clusters.sim_distance)
        clusters.drawdendrogram(clust, self.district_list, jpeg='districts.jpg')
        self.insert_image("districts.jpg")#insert clustered image to canvas

    def cluster_parties(self):
        self.state = "party" #if user clickes cluster parties state changes to party.
        self.analysis_frame.pack(side=TOP, fill=BOTH)
        self.canvas.delete("all") #clearing canvas
        # https://stackoverflow.com/questions/15839491/how-to-clear-tkinter-canvas
        self.party_list, self.district_list, self.data = clusters.readfile("matrix.txt")
        clust = clusters.hcluster(self.data,distance=clusters.sim_distance)
        clusters.drawdendrogram(clust, self.party_list, jpeg='parties.jpg')
        self.insert_image("parties.jpg") #insert clustered image to canvas

    def insert_image(self,name):
        #function to create PIL image and inserting canvas.
        img = Image.open(name)
        self.canvas.img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0,0,image=self.canvas.img,anchor="nw")
        #from link in the pdf related canvas. we need to justify left corner our dendogram to have a nice usage.

    def refined_analysis(self):
        """
        we use try-except structure to raise zero-division error that occurs when user selects less districts
        and let cluster algorithm fail.
        """
        try:
            selected_districts = map(lambda x: self.district_listbox.get(x),self.district_listbox.curselection())
            #we use map function through list of indexes user choosed to get name of districts efficiently.
            if len(selected_districts) == 0: selected_districts = self.data_manager.district_dictionary.keys()
            #if our selection list is empty we tell program to use all of districts.
            self.data_manager.create_matrix(district_list=selected_districts, threshold=self.threshold_combobox.get())
            #executing create_matrix function with selected list and threshold value from combobox.
            if self.state=="district": #here program decides to execute cluster_district or cluster_parties.
                self.cluster_district()
            else:
                self.cluster_parties()
        except:
            raise Exception("You need to select more district to have an refined analysis!.")

class District: #district object as described in pdf
    def __init__(self,district_name,election_results):
        self.district_name = district_name
        self.election_results = election_results

class PoliticalParty: #district object as described in pdf
    def __init__(self,political_party,election_results):
        self.political_party = political_party
        self.election_results = election_results


class DataCenter:
    def __init__(self):
        self.raw_dictionary = dict()
        self.district_dictionary = dict()
        self.political_party_dictionary = dict()

    def txt_manager(self,txtpath): #txt reader function
        """
        Reading algorithm explanation: program read lines and finds Kaynak: YSK line and reads next line of it
        as district name. Then reads irrelevant 6 lines with for loop and starts to read in while True.
        If line is relevant reads line and get values except independent candidates. Else breaks and search next
        Kaynak: YSK line.
        """
        with open(txtpath,"r") as txtfile:
            for line in txtfile:
                line = line.strip()
                if line.endswith("Kaynak: YSK"):
                    election_results = dict()
                    district = txtfile.next().strip()
                    for i in range(6):txtfile.next()  # escaping from irrelevant lines
                    while True:
                        next_line = txtfile.next().strip()
                        if not next_line.startswith("Toplam"):
                            party_splitted = next_line.split("\t")
                            party_name = party_splitted[0]
                            vote_perc = party_splitted[-1]
                            if party_name != "BGMSZ":
                                election_results[party_name] = vote_perc
                        else:break
                    self.raw_dictionary[district] = election_results
        self.create_structures()

    def create_structures(self):
        #fills our attributes with raw dictionary.
        self.create_district_dictionary()
        self.create_party_dictionary()

    def create_district_dictionary(self):
        for key,value in self.raw_dictionary.items():
            district_name = key
            election_results = value
            self.district_dictionary[district_name] = District(district_name=district_name,election_results=election_results)

    def create_party_dictionary(self):
        party_list = list()
        #first collects all parties.
        for value in self.raw_dictionary.values():
            for party in value.keys():
                if party not in party_list: party_list.append(party)
        for party in party_list:#then for each party finds each district and vote percentage.
            election_results = dict()
            for key,value in self.raw_dictionary.items():
                if party in value.keys():
                    vote_perc = value[party]
                    election_results[key] = vote_perc
            self.political_party_dictionary[party] = PoliticalParty(political_party=party,election_results=election_results)

    def create_matrix(self,district_list,threshold):
        threshold = int(threshold.strip("%")) #getting rid of %'s of threshold.
        with open("matrix.txt","w") as matrix:
            matrix.write("Parties")
            for district in district_list:
                matrix.write("\t%s"%district)
            matrix.write("\n")
            for key,value in self.political_party_dictionary.items():
                matrix.write(key)
                party_results = value.election_results
                for district in district_list:
                    if district in party_results.keys():
                        vote = party_results[district].strip("%")
                        if float(vote)>=threshold: #if vote percentage of party is less then threshold
                            matrix.write("\t%s"%vote)
                        else:
                            matrix.write("\t0") #inserts zero to eliminate instead of writing real percentage.
                    else: matrix.write("\t0")
                matrix.write("\n")

def main():
    root.title("Clustering")
    root.geometry("900x620")
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    root = Tk()
    main()
