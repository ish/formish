function count_previous_fields(o) {
  return o.prevAll('.field').length;
}   
   
function create_addlinks(o) {
  o.find('.adder').each(function() {
    $(this).before('<a class="adderlink">Add</a>');
  });
}

function get_sequence_numbers(segments, l) {
  var result = Array();
  for(var i=0; i<segments.length; i++) {
    if (isNaN(parseInt(segments[i])) == false) {
      var segment = segments[i];
      result.push(segment);
    }
  }
  result.push(l);
  return result;
}

function replace_stars(original, nums, divider) {
  var result = Array();
  var segments = original.split(divider);
  var n = 0;

  for(var i=0; i<segments.length; i++) {
    var segment = segments[i];
    if ((segment == '*' || isNaN(parseInt(segment)) == false) && n < nums.length)   {
      // If the segment is a * or a number then we check replace it with the right number (the target number is probably right anyway)
      result.push(nums[n]);
      n=n+1;
    } else {
      // If not then we just push the segment
      result.push(segment);
    }
  }
  return result.join(divider);
}

function construct(start_segments, n, remainder, divider, strip) {
  // Takes a set of prefix segments, a number and the remainder plus a flag whether to strip(?)
  var remainder_bits = remainder.split(divider);
  remainder = remainder_bits.slice(1,remainder_bits.length-strip).join(divider);
  var result = Array();
  for(var i=0; i<start_segments.length; i++) {
    var segment = start_segments[i];
    if (segment != '') {
      result.push(segment);
    }
  }
  result.push(n);
  if (remainder != '') {
      var out = result.join(divider)+divider+remainder;
  } else {
      var out = result.join(divider);
  }
  return out;
}

function convert_id_to_name(s, formid) {
  var segments=s.split('-');
  if (formid == '') {
    var start_segment = 0;
  } else {
    var start_segment = 1;
  }
  var out = segments.slice(start_segment,segments.length).join('.');
  return out;
}

function renumber_sequences(o) {
  o.each( function() {
    var form=$(this);
    renumber_sequence(form);
  });
}

function renumber_sequence(o) {
  var formid = $(o).attr('id');
  var N = {};
  o.find('.type-sequence.widget-sequencedefault').each( function () {
    field_id = $(this).attr('id');
    if ($(this).hasClass('type-container')) {
       var type_container = 0;
    } else {
       var type_container = 1;
    }
    var seqid = $(this).attr('id');
    var seqid_prefix = seqid.substr(0,seqid.length-6);
    // replace id occurences
    $(this).find('.field').each( function () {
        var thisid = $(this).attr('id');
        if (seqid.split('-').length+1 == thisid.split('-').length) {
            if (N[seqid_prefix] == undefined) {
              N[seqid_prefix] = 0;
            } else {
              N[seqid_prefix]=N[seqid_prefix]+1;
            }
            n = N[seqid_prefix];
            var newid = seqid_prefix + n + '--field';
            $(this).attr('id',newid);
            // Replace 'for' occurences
            $(this).find("[for^='"+seqid_prefix+"']").each( function () {
              var name = $(this).attr('for');
              //$(this).text(n);
              var name_remainder = name.substring(seqid_prefix.length, name.length);
              $(this).attr('for', construct(seqid_prefix.split('-'),n,name_remainder,'-', type_container));
            });
            // Replace 'id' occurences
            $(this).find("[id^='"+seqid_prefix+"']").each( function () {
              var name = $(this).attr('id');
              var name_remainder = name.substring(seqid_prefix.length, name.length);
              $(this).attr('id', construct(seqid_prefix.split('-'),n,name_remainder,'-', type_container));
            });
            // replace 'name' occurences
            $(this).find("[name^='"+convert_id_to_name(seqid_prefix, formid)+"']").each( function () {
              var name = $(this).attr('name');
              var name_remainder = name.substring(convert_id_to_name(seqid_prefix, formid).length, name.length);
              $(this).attr('name', construct(convert_id_to_name(seqid_prefix, formid).split('.'),n,name_remainder,'.', type_container));
            });
        }
    });
  });

}

function add_new_item(t,o) {
    var formid = o.attr('id');
    // Get the encoded template
    var code = t.next('.adder').val();
    // Find out how many fields we already have
    var l = count_previous_fields(t.next('.adder'));
    // Get some variable to help with replacing (originalname, originalid, name, id)
    var originalname = t.next('.adder').attr('name');
    var new_originalname = t.closest('.type-container').attr('id');
    new_originalname = new_originalname.substr(0,new_originalname.length-6);
    new_originalname = convert_id_to_name(new_originalname,formid);
    var segments = originalname.split('.');
    // Get the numbers used in the originalname
    var seqnums = get_sequence_numbers(segments, l);
    var originalid = $(o).attr('id')+'-'+segments.join('-');
    segments[ segments.length -1 ] = l;
    var name = segments.join('.');
    var id = $(o).attr('id')+'-'+segments.join('-');
    // Decode the template.
    var html = decodeURIComponent(code);
    // Add the links and mouse clicks to this generated code
    var h = $(html);
    create_addlinks(h);
    add_mouseclick_to_addlinks(h);

    h.find("[name]").each( function () {
      var newname = replace_stars($(this).attr('name'), seqnums, '.');
      $(this).attr('name', newname );
    });
    
    var newid = replace_stars(h.attr('id'),seqnums,'-');

    h.attr('id',newid);
    h.find("[id]").each( function () {
      var newid = replace_stars($(this).attr('id'),seqnums, '-');
      $(this).attr('id', newid );
    });
    h.find("[for]").each( function () {
      var newid = replace_stars($(this).attr('for'),seqnums, '-');
      $(this).attr('for', newid );
      if ($(this).text() == '*') {
        $(this).text(l);
      }
    });
    h.find("label[for='"+id+"']").text(l);
    h.find("legend:contains('*')").text(l);

    t.before(h);
    add_remove_buttons(t.parent().parent());
    add_sortables($('form'));
}

function add_new_items(t,o) {
   var data = t.closest('.field').find('.formish-sequencedata').attr('title').split(',');
   for (var i=0; i<data.length; i++) {
       var terms = data[i].split('=');
       var key = terms[0];
       if (key == 'batch_add_count') {
         var value = terms[1];
         break;
       }
   } 
   for (var i=0; i<value; i++) {
      add_new_item(t,o);
   }
}

function add_mouseclick_to_addlinks(o) {
  o.each( function() {
    var form = $(this);
    form.find('.adderlink').click(function() { add_new_items($(this),form);});
  });
}

function add_remove_buttons(o) {
  o.find('.remove').remove();
  o.find('.seqdelete').each( function() {
    if ($(this).next().text() != 'delete') {
      var x = $('<span class="remove">delete</span>');
      $(this).after(x);
      x.click(function () {
        $(this).closest('.field').remove();
        renumber_sequences($('form'));
        add_sortables($('form'));
      });
    }
  });
}

function order_changed(e,ui) {
    renumber_sequences($('form'));
}

function add_sortables(o) {
  o.find('.sortable .handle').remove();
  o.find('.sortable .seqgrab').after('<div class="handle">drag me</div>');
  o.find('.sortable').sortable({'items':'> .field','stop':order_changed,'handle':'.handle'});
  
}


/* This needs to be run to allow sorting, adding and removing of sequence items */
function formish() {
    add_sortables($('form'));
    create_addlinks($('form'));
    add_mouseclick_to_addlinks($('form'));
    add_remove_buttons($('form'));
}

