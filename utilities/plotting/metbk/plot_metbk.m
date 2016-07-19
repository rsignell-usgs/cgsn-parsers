% load the metbk data for the 4 coastal surface moorings
ce02 = load_parsed('../../../parsed/ce02shsm/D00001/metbk');
ce04 = load_parsed('../../../parsed/ce04ossm/D00001/metbk');
ce07 = load_parsed('../../../parsed/ce07shsm/D00001/metbk');
ce09 = load_parsed('../../../parsed/ce09ossm/D00001/metbk');
%TODO: extend load_parsed to select last N days worth of data

% replace spurious longwave and shortwave irradiance values with NaN
ce02.longwave_irradiance(ce02.longwave_irradiance > 2000) = NaN;
ce04.longwave_irradiance(ce04.longwave_irradiance > 2000) = NaN;
ce07.longwave_irradiance(ce07.longwave_irradiance > 2000) = NaN;
ce09.longwave_irradiance(ce09.longwave_irradiance > 2000) = NaN;

ce02.shortwave_irradiance(ce02.shortwave_irradiance > 2000) = NaN;
ce04.shortwave_irradiance(ce04.shortwave_irradiance > 2000) = NaN;
ce07.shortwave_irradiance(ce07.shortwave_irradiance > 2000) = NaN;
ce09.shortwave_irradiance(ce09.shortwave_irradiance > 2000) = NaN;

% calculate the wind speed and direction (using meterological convention, so
% reverse sign on the vector components before calculating direction).
ce02.wind_speed = sqrt((ce02.northward_wind_velocity.^2 + ce02.eastward_wind_velocity.^2));
ce02.wind_dir = atan2(-1 * ce02.eastward_wind_velocity, -1 * ce02.northward_wind_velocity) * 180/pi;
m = ce02.wind_dir < 0; ce02.wind_dir(m) = ce02.wind_dir(m) + 360;

ce04.wind_speed = sqrt((ce04.northward_wind_velocity.^2 + ce04.eastward_wind_velocity.^2));
ce04.wind_dir = atan2(-1 * ce04.eastward_wind_velocity, -1 * ce04.northward_wind_velocity) * 180/pi;
m = ce04.wind_dir < 0; ce04.wind_dir(m) = ce04.wind_dir(m) + 360;

ce07.wind_speed = sqrt((ce07.northward_wind_velocity.^2 + ce07.eastward_wind_velocity.^2));
ce07.wind_dir = atan2(-1 * ce07.eastward_wind_velocity, -1 * ce07.northward_wind_velocity) * 180/pi;
m = ce07.wind_dir < 0; ce07.wind_dir(m) = ce07.wind_dir(m) + 360;

ce09.wind_speed = sqrt((ce09.northward_wind_velocity.^2 + ce09.eastward_wind_velocity.^2));
ce09.wind_dir = atan2(-1 * ce09.eastward_wind_velocity, -1 * ce09.northward_wind_velocity) * 180/pi;
m = ce09.wind_dir < 0; ce09.wind_dir(m) = ce09.wind_dir(m) + 360;

% calculate the surface salinity values using the TEOS-10 toolbox
ce02.sea_surface_salinity = gsw_SP_from_C(ce02.sea_surface_conductivity * 10, ...
    ce02.sea_surface_temperature, gsw_p_from_z(1.5, 44.6384));

ce04.sea_surface_salinity = gsw_SP_from_C(ce04.sea_surface_conductivity * 10, ...
    ce04.sea_surface_temperature, gsw_p_from_z(1.5, 46.9868));

ce07.sea_surface_salinity = gsw_SP_from_C(ce07.sea_surface_conductivity * 10, ...
    ce07.sea_surface_temperature, gsw_p_from_z(1.5, 44.3662));

ce09.sea_surface_salinity = gsw_SP_from_C(ce09.sea_surface_conductivity * 10, ...
    ce09.sea_surface_temperature, gsw_p_from_z(1.5, 46.8513));

% convert the buoy time records from an epoch time stamp (seconds since
% 1970-01-01 UTC) to a Matlab recognized date number.
time_ref = datenum(1970, 1, 1, 0, 0, 0);
ce02.time = (double(ce02.time) / 60 / 60 / 24) + time_ref;
ce04.time = (double(ce04.time) / 60 / 60 / 24) + time_ref;
ce07.time = (double(ce07.time) / 60 / 60 / 24) + time_ref;
ce09.time = (double(ce09.time) / 60 / 60 / 24) + time_ref;

% set the date ranges
minx = datenum(2015,3,31,23,30,0);
maxx = floor(now) + 1 + (30 / 60 / 24);

% Create hourly averaged data
hourly = [ce02.time; ce02.barometric_pressure; ce02.relative_humidity; 
    ce02.precipitation_level; ce02.longwave_irradiance; ce02.shortwave_irradiance;
    ce02.air_temperature; ce02.sea_surface_temperature; ce02.sea_surface_conductivity;
    ce02.sea_surface_salinity; ce02.eastward_wind_velocity; ce02.northward_wind_velocity];
ce02.hourly = bin(hourly',1,minx,maxx,1/24,'median');

hourly = [ce04.time; ce04.barometric_pressure; ce04.relative_humidity; 
    ce04.precipitation_level; ce04.longwave_irradiance; ce04.shortwave_irradiance;
    ce04.air_temperature; ce04.sea_surface_temperature; ce04.sea_surface_conductivity;
    ce04.sea_surface_salinity; ce04.eastward_wind_velocity; ce04.northward_wind_velocity];
ce04.hourly = bin(hourly',1,minx,maxx,1/24,'median');

hourly = [ce07.time; ce07.barometric_pressure; ce07.relative_humidity; 
    ce07.precipitation_level; ce07.longwave_irradiance; ce07.shortwave_irradiance;
    ce07.air_temperature; ce07.sea_surface_temperature; ce07.sea_surface_conductivity;
    ce07.sea_surface_salinity; ce07.eastward_wind_velocity; ce07.northward_wind_velocity];
ce07.hourly = bin(hourly',1,minx,maxx,1/24,'median');

hourly = [ce09.time; ce09.barometric_pressure; ce09.relative_humidity; 
    ce09.precipitation_level; ce09.longwave_irradiance; ce09.shortwave_irradiance;
    ce09.air_temperature; ce09.sea_surface_temperature; ce09.sea_surface_conductivity;
    ce09.sea_surface_salinity; ce09.eastward_wind_velocity; ce09.northward_wind_velocity];
ce09.hourly = bin(hourly',1,minx,maxx,1/24,'median');
clear hourly

% re-calculate the wind speed and direction from the hourly averaged wind vector
% components.
ce02.hourly(:,13) = sqrt((ce02.hourly(:,12).^2 + ce02.hourly(:,11).^2));
ce02.hourly(:,14) = atan2(-1 * ce02.hourly(:,11), -1 * ce02.hourly(:,12)) * 180/pi;
m = ce02.hourly(:,14) < 0; ce02.hourly(m,14) = ce02.hourly(m,14) + 360;

ce04.hourly(:,13) = sqrt((ce04.hourly(:,12).^2 + ce04.hourly(:,11).^2));
ce04.hourly(:,14) = atan2(-1 * ce04.hourly(:,11), -1 * ce04.hourly(:,12)) * 180/pi;
m = ce04.hourly(:,14) < 0; ce04.hourly(m,14) = ce04.hourly(m,14) + 360;

ce07.hourly(:,13) = sqrt((ce07.hourly(:,12).^2 + ce07.hourly(:,11).^2));
ce07.hourly(:,14) = atan2(-1 * ce07.hourly(:,11), -1 * ce07.hourly(:,12)) * 180/pi;
m = ce07.hourly(:,14) < 0; ce07.hourly(m,14) = ce07.hourly(m,14) + 360;

ce09.hourly(:,13) = sqrt((ce09.hourly(:,12).^2 + ce09.hourly(:,11).^2));
ce09.hourly(:,14) = atan2(-1 * ce09.hourly(:,11), -1 * ce09.hourly(:,12)) * 180/pi;
m = ce09.hourly(:,14) < 0; ce09.hourly(m,14) = ce09.hourly(m,14) + 360;

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

% create Matlab date numbers from the individual time components of the NDBC
% records
time = datenum(oregon(:,1),oregon(:,2),oregon(:,3),oregon(:,4),oregon(:,5),0);
oregon = [time oregon];

time = datenum(wash(:,1),wash(:,2),wash(:,3),wash(:,4),wash(:,5),0);
wash = [time wash];
clear time

% plot the data for review -- oregon and washington separately
figure(1)
orient portrait

subplot(811)
scatter(oregon(:,1),oregon(:,7),'filled','k')
hold on
scatter(ce02.hourly(:,1), ce02.hourly(:,14), 'filled','g')
scatter(ce04.hourly(:,1), ce04.hourly(:,14), 'filled','b')
datetick('x','mm/dd','keeplimits')
title('Wind Direction')
ylabel('degress')
xlim([minx maxx]); ylim([0 360])
box on

subplot(812)
plot(oregon(:,1),oregon(:,8),'k',ce02.hourly(:,1),ce02.hourly(:,13),'g',...
    ce04.hourly(:,1),ce04.hourly(:,13),'b')
datetick('x','mm/dd','keeplimits')
title('Wind Speed')
ylabel('m/s')
xlim([minx maxx]); ylim([0 20])
box on

subplot(813)
plot(oregon(:,1),oregon(:,14),'k',ce02.hourly(:,1),ce02.hourly(:,2),'g',...
    ce04.hourly(:,1),ce04.hourly(:,2),'b')
datetick('x','mm/dd','keeplimits')
title('Barometric Pressure')
ylabel('mbar')
xlim([minx maxx]); ylim([1000 1050])
box on

subplot(814)
plot(oregon(:,1),oregon(:,15),'k',ce02.hourly(:,1),ce02.hourly(:,7),'g',...
    ce04.hourly(:,1),ce04.hourly(:,7),'b')
datetick('x','mm/dd','keeplimits')
title('Air Temperature')
ylabel('^oC')
xlim([minx maxx]); ylim([5 20])
box on

subplot(815)
plot(oregon(:,1),oregon(:,16),'k',ce02.hourly(:,1),ce02.hourly(:,8),'g',...
    ce04.hourly(:,1),ce04.hourly(:,8),'b')
datetick('x','mm/dd','keeplimits')
title('Sea Surface Temperature')
ylabel('^oC')
xlim([minx maxx]); ylim([5 15])
box on

subplot(816)
plot(ce02.hourly(:,1),ce02.hourly(:,10),'g',...
    ce04.hourly(:,1),ce04.hourly(:,10),'b')
datetick('x','mm/dd','keeplimits')
title('Salinity')
ylabel('psu')
xlim([minx maxx]); ylim([25 35])
box on

subplot(817)
plot(ce02.hourly(:,1),ce02.hourly(:,6),'g',...
    ce04.hourly(:,1),ce04.hourly(:,6),'b')
datetick('x','mm/dd','keeplimits')
title('Shortwave Radiation')
ylabel('W/m^2')
xlim([minx maxx]); ylim([0 1000])
box on

subplot(818)
plot(ce02.hourly(:,1),ce02.hourly(:,5)*NaN,'k',...
    ce02.hourly(:,1),ce02.hourly(:,5),'g',...
    ce04.hourly(:,1),ce04.hourly(:,5),'b')
datetick('x','mm/dd','keeplimits')
title('Longwave Radiation')
ylabel('W/m^2')
xlim([minx maxx]); ylim([200 500])
legend('46050','CE02SHSM','CE04OSSM','Location','West')
box on

set(gcf,'color','w')
set(gcf,'PaperUnits','inches','PaperPosition',[0.25 0.25 8 10.5])
print(gcf,'-dpng','-r300','oregon_comparisons.png')

figure(2)
orient portrait

subplot(811)
scatter(wash(:,1),wash(:,7),'filled','k')
hold on
scatter(ce07.hourly(:,1), ce07.hourly(:,14), 'filled','g')
scatter(ce09.hourly(:,1), ce09.hourly(:,14), 'filled','b')
datetick('x','mm/dd','keeplimits')
title('Wind Direction')
ylabel('degress')
xlim([minx maxx]); ylim([0 360])
box on

subplot(812)
plot(wash(:,1),wash(:,8),'k',ce07.hourly(:,1),ce07.hourly(:,13),'g',...
    ce09.hourly(:,1),ce09.hourly(:,13),'b')
datetick('x','mm/dd','keeplimits')
title('Wind Speed')
ylabel('m/s')
xlim([minx maxx]); ylim([0 20])
box on

subplot(813)
plot(wash(:,1),wash(:,14),'k',ce07.hourly(:,1),ce07.hourly(:,2),'g',...
    ce09.hourly(:,1),ce09.hourly(:,2),'b')
datetick('x','mm/dd','keeplimits')
title('Barometric Pressure')
ylabel('mbar')
xlim([minx maxx]); ylim([1000 1050])
box on

subplot(814)
plot(wash(:,1),wash(:,15),'k',ce07.hourly(:,1),ce07.hourly(:,7),'g',...
    ce09.hourly(:,1),ce09.hourly(:,7),'b')
datetick('x','mm/dd','keeplimits')
title('Air Temperature')
ylabel('^oC')
xlim([minx maxx]); ylim([5 20])
box on

subplot(815)
plot(wash(:,1),wash(:,16),'k',ce07.hourly(:,1),ce07.hourly(:,8),'g',...
    ce09.hourly(:,1),ce09.hourly(:,8),'b')
datetick('x','mm/dd','keeplimits')
title('Sea Surface Temperature')
ylabel('^oC')
xlim([minx maxx]); ylim([5 15])
box on

subplot(816)
plot(ce07.hourly(:,1),ce07.hourly(:,10),'g',...
    ce09.hourly(:,1),ce09.hourly(:,10),'b')
datetick('x','mm/dd','keeplimits')
title('Salinity')
ylabel('psu')
xlim([minx maxx]); ylim([25 35])
box on

subplot(817)
plot(ce07.hourly(:,1),ce07.hourly(:,6),'g',...
    ce09.hourly(:,1),ce09.hourly(:,6),'b')
datetick('x','mm/dd','keeplimits')
title('Shortwave Radiation')
ylabel('W/m^2')
xlim([minx maxx]); ylim([0 1000])
box on

subplot(818)
plot(ce07.hourly(:,1),ce07.hourly(:,5)*NaN,'k',...
    ce07.hourly(:,1),ce07.hourly(:,5),'g',...
    ce09.hourly(:,1),ce09.hourly(:,5),'b')
datetick('x','mm/dd','keeplimits')
title('Longwave Radiation')
ylabel('W/m^2')
xlim([minx maxx]); ylim([200 500])
legend('46029','CE07SHSM','CE09OSSM','Location','West')
box on

set(gcf,'color','w')
set(gcf,'PaperUnits','inches','PaperPosition',[0.25 0.25 8 10.5])
print(gcf,'-dpng','-r300','washington_comparisons.png')
