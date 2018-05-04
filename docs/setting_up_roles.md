# Setting Up Primary Roles

Superset has a permission system built-in based on the underlying Flask AppBuilder security API.  The FAB Security model aims to be pretty
fine-grained, which can be both a blessing and a curse.

Superset recommends that you do not alter the default roles and they suggest that you instead give most users a base "Gamma" role and extend
it by union'ing in other roles.  There is not at this time much guidance in terms of how to programatically manage roles. Another pain point
is that you end up with a huge jumble of permissions per role and it is not easy to tell which permissions relate specifically relate to any given view
within the site.

The following is intended as a starting point for initial exploration and testing of the site.  Some attempt has been made to remove edit / delete
actions from the Viewer role while preserving the ability to view Dashboards and Charts.  More work may be needed to remove other permissions not
suitable for this role.  In some cases an 'edit' button may display but the user does not have permission and will be redirected elsewhere. However the UI
would need some attention here.

## Create Viewer Role

First create a copy of the default `Gamma` role.

1. Select the `Gamma` role in http://localhost:9090/roles/list/ and use the **Copy** command in the **Actions** menu at the bottom of page
name the new Role as _Viewer_
1. In the roles list, find "Gamma copy" and click its edit button
1. In `Permissions` field, add `all datasource access on all all_datasource_access`
1. In the `Name` field change it to "Viewer", then Save
1. Run the following SQL statements against the `superset` database to purge the Viewer role of edit/remove permissions:

```
-- remove can delete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_delete")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can add
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_add")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can add slices
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_add_slices")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can copy dash
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_copy_dash")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can delete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_delete")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can edit
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_edit")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can import dashboards
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "can_import_dashboards")) and role_id = (select id from ab_role where name = "Viewer");

-- remove can override role permissions
-- role will not any by default

-- remove muldelete
delete from ab_permission_view_role where permission_view_id in (select id from ab_permission_view where permission_id = (select id from ab_permission where name = "muldelete")) and role_id = (select id from ab_role where name = "Viewer");

```

## Create Editor Role

Create a copy of the default `Alpha` role.

1. Select the `Alpha` role in http://localhost:9090/roles/list/ and use the **Copy** command in the **Actions** menu at the bottom of page
1. In the roles list, find "Alpha copy" and click its edit button
1. In the `Name` field change it to "Editor", then Save

```
-- adds SQL Lab permissions
insert into ab_permission_view_role (permission_view_id, role_id)
  select apv.id, ar.id from ab_permission_view as apv
  inner join ab_role as ar on ar.name = "Editor"
  where apv.id in (select permission_view_id from ab_permission_view_role where role_id = (select id from ab_role where name = "sql_lab"));
```
