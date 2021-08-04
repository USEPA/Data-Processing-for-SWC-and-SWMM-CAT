import os,sys,arcpy;
import http.client,json,csv;
import zipfile,requests,shutil;

def rez():
    
    rez = {};
    
    # Verify or Create Source filegeodatabase
    rez['source'] = os.getcwd() + os.sep + 'source.gdb';

    if not arcpy.Exists(rez['source']):
        print("  creating new source workspace");
        arcpy.CreateFileGDB_management(
             os.path.dirname(rez['source'])
            ,os.path.basename(rez['source'])
        );
        
    # Verify or Create Working filegeodatabase
    rez['working'] = os.getcwd() + os.sep + 'working.gdb';

    if not arcpy.Exists(rez['working']):
        print("  creating new working workspace");
        arcpy.CreateFileGDB_management(
             os.path.dirname(rez['working'])
            ,os.path.basename(rez['working'])
        );
        
    # Verify or Create Results filegeodatabase
    rez['results'] = os.getcwd() + os.sep + 'results.gdb';

    if not arcpy.Exists(rez['results']):
        print("  creating new results workspace");
        arcpy.CreateFileGDB_management(
             os.path.dirname(rez['results'])
            ,os.path.basename(rez['results'])
        );

    # Verify or Create qa directory
    rez['qa'] = os.getcwd() + os.sep + 'qa';

    if not arcpy.Exists(rez['qa']):
        print("  creating new qa directory");
        os.mkdir(rez['qa']);
        
    # Verify or Create resources directory
    rez['resources'] = os.getcwd() + os.sep + 'resources';

    if not arcpy.Exists(rez['resources']):
        print("  creating new resources directory");
        os.mkdir(rez['resources']);
        
    # Verify existence of files directory
    rez['files'] = os.getcwd() + os.sep + 'files';
    
    if not arcpy.Exists(rez['resources']):
        raise Exception('ERROR: project files directory not found');
        
    return rez;

def scrape_ags(host,path,fgdb,fc,forcelimit=None):
    
    if arcpy.Exists(fgdb + os.sep + fc):
        arcpy.Delete_management(fgdb + os.sep + fc);
        
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"};
    conn = http.client.HTTPSConnection(host);
    conn.request("POST",path,"f=json",headers);
    response = conn.getresponse();
    data = response.read();
    json_data = json.loads(data);
    if not 'currentVersion' in json_data:
        raise ValueError("Error, unable to query https://" + host + path);
    extraction_amount = json_data['maxRecordCount'];
    if forcelimit is not None and forcelimit < extraction_amount:
        extraction_amount = forcelimit;
    where = "1=1";
    params = "where={}&returnIdsOnly=true&returnGeometry=false&f=json".format(where);
    conn = http.client.HTTPSConnection(host);
    conn.request("POST",path + "/query",params,headers);
    response = conn.getresponse();
    data = response.read();
    json_data = json.loads(data);
    ary_oid   = sorted(json_data['objectIds']);
    oid_name  = json_data['objectIdFieldName'];
    oid_count = len(ary_oid);
    
    initial_hit = True;
    counter = 0;
    while counter <= oid_count - 1:
        if counter + extraction_amount > oid_count - 1:
            int_max = oid_count - 1;
        else:
            int_max = counter + extraction_amount - 1;
        where = oid_name + ' >= ' + str(ary_oid[counter]) + ' AND ' + oid_name + ' <= ' + str(ary_oid[int_max]);
        
        fields = "*";
        params = "where={}&outFields={}&returnGeometry=true&outSR=4269&f=json".format(where, fields);
        conn = http.client.HTTPSConnection(host);
        conn.request("POST",path + "/query",params,headers);
        response = conn.getresponse();
        data = response.read(); 
        json_data = json.loads(data);
        ef = arcpy.AsShape(json_data,True);
        if initial_hit:
            arcpy.management.CopyFeatures(ef,fgdb + os.sep + fc)
            initial_hit = False;
        else:
            arcpy.Append_management(ef,fgdb + os.sep + fc,"NO_TEST");
        counter += extraction_amount;
        
    conn.close(); 
    del conn;

    return True;
    
def downloadtab(url,filename):
    if arcpy.Exists(filename):
        arcpy.Delete_management(filename);
    print("  downloading file");
    with open(filename,'wb') as f,requests.get(url,stream=True) as r:
        for line in r.iter_lines():
            f.write(line + '\n'.encode());
    return True;
    
def tab2fc(filename,fgdb,fc,longname,latname,field_mapping=None):
    
    if arcpy.Exists('memory' + os.sep + 'tempTable'):
        arcpy.Delete_management('memory' + os.sep + 'tempTable');
  
    print("  loading to table");
    arcpy.TableToTable_conversion(
         in_rows       = filename
        ,out_path      = 'memory'
        ,out_name      = 'tempTable'
        ,field_mapping = field_mapping
    );
    
    if arcpy.Exists(fgdb + os.sep + fc):
        arcpy.Delete_management(fgdb + os.sep + fc);
        
    print("  converting to NAD83 points");
    arcpy.management.XYTableToPoint(
         in_table          = 'memory' + os.sep + 'tempTable'
        ,out_feature_class = fgdb + os.sep + fc
        ,x_field           = longname
        ,y_field           = latname
        ,coordinate_system = arcpy.SpatialReference(4269)
    );
    
    arcpy.Delete_management('memory' + os.sep + 'tempTable');
    return True;

def tab2tab(filename,fgdb,fc,field_mapping=None):
    
    if arcpy.Exists(fgdb + os.sep + fc):
        arcpy.Delete_management(fgdb + os.sep + fc);
    
    print("  loading to table");
    arcpy.TableToTable_conversion(
         in_rows       = filename
        ,out_path      = fgdb
        ,out_name      = fc
        ,field_mapping = field_mapping
    );
        
    return True;

def fmtext(infc,fieldname,fieldlength):
    fm = arcpy.FieldMap();
    fm.addInputField(infc,fieldname);
    nf = fm.outputField;
    nf.type = 'Text';
    nf.length = fieldlength;
    fm.outputField = nf;
    return fm;

def fmint(infc,fieldname):
    fm = arcpy.FieldMap();
    fm.addInputField(infc,fieldname);
    nf = fm.outputField;
    nf.type = 'Integer';
    fm.outputField = nf;
    return fm;

def fmdouble(infc,fieldname):
    fm = arcpy.FieldMap();
    fm.addInputField(infc,fieldname);
    nf = fm.outputField;
    nf.type = 'Double';
    fm.outputField = nf;
    return fm;
    
def fetchResource(data,fgdb):
    
    if 'zipdr' in data and data['zipdr'] is not None:
        zipshp = data['zipdr'] + '/' + data['shp'];
    else:
        zipshp = data['shp'];
        
    if 'query' in data:
        query = data['query'];
    else:
        query = None;
        
    if 'fix' in data:
        fix = data['fix'];
    else:
        fix = data['shp'];
    
    file = os.getcwd() + os.sep + data['file'];

    if not os.path.exists(file):
        
        r = requests.get(
             url    = data['url']
            ,stream = True
            ,verify = True
        );
        
        with open(file,'wb') as f:
            for chunk in r.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk);
    
    if arcpy.Exists(arcpy.env.scratchFolder + os.sep + data['shp'] + '.shp'):
        arcpy.Delete_management(arcpy.env.scratchFolder + os.sep + data['shp'] + '.shp');
        
    with zipfile.ZipFile(file) as zf:
        
        for ext in ['.dbf','.prj','sbn','.sbx','.shp','.shx']:
            if zipshp + ext in zf.namelist():
                with zf.open(zipshp + ext) as s:
                    with open(arcpy.env.scratchFolder + os.sep + fix + ext,'wb') as t:
                        shutil.copyfileobj(s,t);
        
    if arcpy.Exists(fgdb + os.sep + fix):
        arcpy.Delete_management(fgdb + os.sep + fix);

    arcpy.conversion.FeatureClassToFeatureClass(
         in_features  = arcpy.env.scratchFolder + os.sep + fix + '.shp'
        ,out_path     = fgdb
        ,out_name     = fix
        ,where_clause = query
    );
    
    arcpy.management.RepairGeometry(
         in_features = fgdb + os.sep + fix
        ,delete_null = 'DELETE_NULL'
    );
    
def tabWriter(fc,outfile,flds,outflds=None):

    if outflds is None:
        outflds = flds;
        
    with open(outfile,'w',newline='',encoding='utf-8') as f:
        writer = csv.writer(f,delimiter='\t',lineterminator='\n');

        with arcpy.da.SearchCursor(fc,flds) as incur:
            writer.writerow(outflds);

            for row in incur:
                if row[0] is not None:
                    writer.writerow(row);

    cnt = arcpy.GetCount_management(outfile)[0];         
    print("  wrote " + str(cnt) + " records to " + os.path.basename(outfile) + ".");
