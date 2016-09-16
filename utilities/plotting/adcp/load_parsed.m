function data = load_parsed(parsed_dir)

% list the parsed data files for the coastal surface moorings
files = dir([parsed_dir, '/*.mat']);

% and load the data into a single structured array (skipping character arrays)
data = load([parsed_dir, '/', files(1).name], '-mat', ...
    '-regexp', '^(?!dcl_date_time_string|date_string|time_string|serial_number).');
vrs = fieldnames(data);
for i = 2:length(files)
    tmp = load([parsed_dir, '/', files(i).name], '-mat', ...
        '-regexp', '^(?!dcl_date_time_string|date_string|time_string|serial_number).');
    if isequal(vrs, fieldnames(tmp))
        for k = 1:length(vrs)
            data.(vrs{k}) = [data.(vrs{k}) tmp.(vrs{k})];
        end %for
    end %if
end
clear files i tmp k
