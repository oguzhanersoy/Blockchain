nodes=[100,200,500,1000,2000,5000,10000];
connections=[8,16];

epsilon=0.1;

APL_c8=[1.87,2.14,2.45,2.65,2.81,3.03,3.22];
ANV_c8=[11,12,14,15,16,18,19.75]./nodes;

APL_c16=[1.72,1.87,2.09,2.30,2.50,2.72,2.84];
ANV_c16=[20.2,23,25,27,29,32,34]./nodes;

Trails_c8=[1000,1000,1000,1000,1000,1000,100]*100;
Trails_c16=[2000,2000,1000,1000,2000,1000,100]*100;

Fail1_c8=[27,83,302,603,1087,1573,134]./Trails_c8;
Fail2_c8=[270,671,1628,2765,3625,5488,894]./Trails_c8;
Fail3_c8=[1075,2716,4932,7839,10261,14701,1822]./Trails_c8;

Fail1_c16=[NaN,NaN,NaN,3,5,11,1]./Trails_c16;
Fail2_c16=[2,3,10,49,157,124,13]./Trails_c16;
Fail3_c16=[31,87,147,342,936,1032,231]./Trails_c16;

%graph1=plot(nodes,Fail1_c8,'o-r',nodes,Fail2_c8,'*-g',nodes,Fail3_c8,'d-b',nodes,Fail1_c16,'o--r',nodes,Fail2_c16,'*--g',nodes,Fail3_c16,'d--b');
%legend("h=0.2, N_{con}=8","h=0.3, N_{con}=8","h=0.4, N_{con}=8","h=0.2, N_{con}=16","h=0.3, N_{con}=16","h=0.4, N_{con}=16");
%xlabel('Number of nodes');
%ylabel('Probability of a failure');
%set(graph1,'LineWidth',2);
%set(graph1,'MarkerSize',10);
graph1=plot(nodes,Fail2_c8,'*-g',nodes,Fail3_c8,'d-b',nodes,Fail2_c16,'*--g',nodes,Fail3_c16,'d--b');
legend("h=0.3, N_{con}=8","h=0.4, N_{con}=8","h=0.3, N_{con}=16","h=0.4, N_{con}=16");
xlabel('Number of nodes');
ylabel('Probability of a failure');
set(graph1,'LineWidth',3);
set(graph1,'MarkerSize',15);
%hold on
%plot(nodes,Fail1_c16,'o--r',nodes,Fail2_c16,'*--g',nodes,Fail3_c16,'d--b')
%legend("h=0.2,N_con=16","h=0.3,N_con=16","h=0.4,N_con=16");
figure,graph2=plot(nodes,100*(1-ANV_c8),nodes,100*(1-ANV_c16));
%hold on
%plot(nodes,100*(1-ANV_c16))
figure,graph3=plot(nodes,(ANV_c8).*nodes,'^-r',nodes,(ANV_c16).*nodes,'^--g',nodes,nodes,'^:b');
xlabel('Number of nodes');
ylabel('Bandwith Usage');
set(graph3,'LineWidth',3);
set(graph3,'MarkerSize',15);
legend("Our Routing with N_{con}=8","Our Routing with N_{con}=16","Standard Routing")