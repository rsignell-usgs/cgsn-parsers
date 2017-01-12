% load the metbk data for the 4 coastal surface moorings
ce02 = load_parsed('../../../parsed/ce02shsm/D00001/wavss');
ce04 = load_parsed('../../../parsed/ce04ossm/D00001/wavss');
ce07 = load_parsed('../../../parsed/ce07shsm/D00001/wavss');
ce09 = load_parsed('../../../parsed/ce09ossm/D00001/wavss');
%TODO: extend load_parsed to select last N days worth of data

% convert the buoy time records from an epoch time stamp (seconds since
% 1970-01-01 UTC) to a Matlab recognized date number.
time_ref = datenum(1970, 1, 1, 0, 0, 0);
ce02.time = (double(ce02.time) / 60 / 60 / 24) + time_ref;
ce04.time = (double(ce04.time) / 60 / 60 / 24) + time_ref;
ce07.time = (double(ce07.time) / 60 / 60 / 24) + time_ref;
ce09.time = (double(ce09.time) / 60 / 60 / 24) + time_ref;

% Load the NDBC standard meterological data from the NDBC buoys off of Oregon
% and Washington for the last 45 days.
unix('rm -f 46050.txt');
[status, ~] = unix('wget http://www.ndbc.noaa.gov/data/realtime2/46050.txt');
if status == 0
    [oregon, vars] = importNDBC('46050.txt');
end %if

unix('rm -f 46029.txt');
[status, ~] = unix('wget http://www.ndbc.noaa.gov/data/realtime2/46029.txt');
if status == 0
    wash = importNDBC('46029.txt');
end %if
clear status

unix('rm -f 46211.txt');
[status, ~] = unix('wget http://www.ndbc.noaa.gov/data/realtime2/46211.txt');
if status == 0
    cdip = importNDBC('46211.txt');
end %if
clear status

% create Matlab date numbers from the individual time components of the NDBC
% records
time = datenum(oregon(:,1),oregon(:,2),oregon(:,3),oregon(:,4),oregon(:,5),0);
oregon = [time oregon];

time = datenum(wash(:,1),wash(:,2),wash(:,3),wash(:,4),wash(:,5),0);
wash = [time wash];

time = datenum(cdip(:,1),cdip(:,2),cdip(:,3),cdip(:,4),cdip(:,5),0);
cdip = [time cdip];
clear time

% plot the data for review -- oregon and washington separately
minx = datenum(2015,3,31,23,30,0);
maxx = floor(now) + 1 + (30 / 60 / 24);

figure(1)
orient portrait

subplot(411)
plot(oregon(:,1),oregon(:,10),'k', ...
    ce02.time, ce02.significant_wave_height,'g', ...
    ce04.time, ce04.significant_wave_height,'b')
datetick('x','mm/dd','keeplimits')
title('Significant Wave Height')
ylabel('meters')
xlim([minx maxx]); ylim([0 10])
box on

subplot(412)
plot(oregon(:,1),oregon(:,11),'k', ...
    ce02.time, ce02.peak_period,'g', ...
    ce04.time, ce04.peak_period,'b')
datetick('x','mm/dd','keeplimits')
title('Dominant Wave Period')
ylabel('seconds')
xlim([minx maxx]); ylim([0 30])
box on

subplot(413)
plot(oregon(:,1),oregon(:,12),'k', ...
    ce02.time, ce02.average_wave_period,'g', ...
    ce04.time, ce04.average_wave_period,'b')
datetick('x','mm/dd','keeplimits')
title('Average Wave Period')
ylabel('seconds')
xlim([minx maxx]); ylim([0 30])
box on

subplot(414)
plot(oregon(:,1),oregon(:,13),'k', ...
    ce02.time, ce02.mean_wave_direction,'g', ...
    ce04.time, ce04.mean_wave_direction,'b')
datetick('x','mm/dd','keeplimits')
title('Mean Wave Direction')
ylabel('degrees')
xlim([minx maxx]); ylim([0 360])
legend('46050','CE02SHSM','CE04OSSM','Location','SouthWest')
box on

set(gcf,'color','w')
set(gcf,'PaperUnits','inches','PaperPosition',[0.25 0.25 8 10.5])
print(gcf,'-dpng','-r300','oregon_wavss_comparisons.png')

figure(2)
orient portrait

subplot(411)
plot(wash(:,1),wash(:,10),'k',cdip(:,1),cdip(:,10),'r', ...
    ce07.time, ce07.significant_wave_height,'g', ...
    ce09.time, ce09.significant_wave_height,'b')
datetick('x','mm/dd','keeplimits')
title('Significant Wave Height')
ylabel('meters')
xlim([minx maxx]); ylim([0 10])
box on

subplot(412)
plot(wash(:,1),wash(:,11),'k',cdip(:,1),cdip(:,11),'r', ...
    ce07.time, ce07.peak_period,'g', ...
    ce09.time, ce09.peak_period,'b')
datetick('x','mm/dd','keeplimits')
title('Dominant Wave Period')
ylabel('seconds')
xlim([minx maxx]); ylim([0 30])
box on

subplot(413)
plot(wash(:,1),wash(:,12),'k',cdip(:,1),cdip(:,12),'r', ...
    ce07.time, ce07.average_wave_period,'g', ...
    ce09.time, ce09.average_wave_period,'b')
datetick('x','mm/dd','keeplimits')
title('Average Wave Period')
ylabel('seconds')
xlim([minx maxx]); ylim([0 30])
box on

subplot(414)
plot(wash(:,1),wash(:,13),'k',cdip(:,1),cdip(:,13),'r', ...
    ce07.time, ce07.mean_wave_direction,'g', ...
    ce09.time, ce09.mean_wave_direction,'b')
datetick('x','mm/dd','keeplimits')
title('Mean Wave Direction')
ylabel('degrees')
xlim([minx maxx]); ylim([0 360])
legend('46029','46211','CE07SHSM','CE09OSSM','Location','SouthWest')
box on

set(gcf,'color','w')
set(gcf,'PaperUnits','inches','PaperPosition',[0.25 0.25 8 10.5])
print(gcf,'-dpng','-r300','wash_wavss_comparisons.png')
